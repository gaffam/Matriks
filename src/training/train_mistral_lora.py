"""Simple QLoRA training script for Google Colab.

This script loads a JSONL instruction dataset and fine-tunes a Mistral model
using HuggingFace Transformers and PEFT. The resulting LoRA weights are saved
under ``output_dir``. After training you can convert ``pytorch_model.bin`` to
GGUF using the ``convert_to_gguf.sh`` helper.
"""

import argparse
from pathlib import Path
import logging

from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
)
from peft import get_peft_model, LoraConfig, prepare_model_for_kbit_training
from huggingface_hub import HfApi


def build_text(example: dict) -> str:
    """Return the concatenated training text for a single example.

    The dataset may contain either ``output`` or legacy ``response`` keys. This
    helper normalizes them so training doesn't fail when older datasets are
    used.
    """

    output = example.get("output") or example.get("response", "")
    return (
        example.get("instruction", "")
        + "\n"
        + example.get("input", "")
        + "\n"
        + output
    )


def main() -> None:
    """Run a minimal QLoRA fine-tuning loop."""

    parser = argparse.ArgumentParser()
    parser.add_argument("data_path", help="Path to JSONL dataset")
    parser.add_argument("--output_dir", default="finetuned")
    parser.add_argument(
        "--base_model",
        default="mistralai/Mistral-7B-v0.1",
        help="HuggingFace model name",
    )
    parser.add_argument("--push", help="Hugging Face repo id to upload", default=None)
    args = parser.parse_args()

    ds = load_dataset("json", data_files=args.data_path)["train"]

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        device_map="auto",
        load_in_4bit=True,
    )
    model = prepare_model_for_kbit_training(model)
    lora_cfg = LoraConfig(task_type="CAUSAL_LM", r=8, lora_alpha=16, lora_dropout=0.05)
    model = get_peft_model(model, lora_cfg)

    def tokenize(batch):
        """Tokenize a batch from the dataset."""
        text = build_text(batch)
        return tokenizer(text, truncation=True, padding="max_length")

    tokenized = ds.map(tokenize, batched=True)

    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=args.output_dir,
            per_device_train_batch_size=1,
            num_train_epochs=3,
            report_to="none",
        ),
        train_dataset=tokenized,
    )
    trainer.train()

    model.save_pretrained(args.output_dir, safe_serialization=True)
    tokenizer.save_pretrained(args.output_dir)

    if args.push:
        api = HfApi()
        weights = Path(args.output_dir) / "pytorch_model.safetensors"
        api.upload_file(path_or_fileobj=str(weights), path_in_repo="pytorch_model.safetensors", repo_id=args.push, repo_type="model")
        logging.info("LoRA weights uploaded to https://huggingface.co/%s", args.push)

    logging.info(
        "Training complete. Convert to GGUF with: ./convert_to_gguf.sh %s/pytorch_model.safetensors models/finetuned-mistral.gguf",
        args.output_dir,
    )


if __name__ == "__main__":
    main()
