import json
import logging
from pathlib import Path

import torch
from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import pytesseract

try:
    from invoice2data import extract_data
    from invoice2data.extract.loader import read_templates
    INVOICE2DATA_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    INVOICE2DATA_AVAILABLE = False


class InvoiceParser:
    """Extract structured info from invoice images using a Donut model."""

    def __init__(self, model_name="naver-clova-ix/donut-base", templates_dir: str | None = None):
        self.use_donut = torch.cuda.is_available()
        self.templates = None
        if INVOICE2DATA_AVAILABLE and templates_dir:
            try:
                self.templates = read_templates(templates_dir)
            except Exception:
                pass
        if self.use_donut:
            self.processor = DonutProcessor.from_pretrained(model_name)
            self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
            self.device = "cuda"
            self.model.to(self.device)
            logging.info(
                "Invoice parser ready with %s on %s", model_name, self.device
            )
        else:
            logging.warning("CUDA not available, falling back to Tesseract")
            self.device = "cpu"

    def parse_invoice(self, image_path: str) -> dict:
        """Process an image or PDF file and return invoice info as JSON."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(str(path))
        if INVOICE2DATA_AVAILABLE and path.suffix.lower() == ".pdf":
            try:
                data = extract_data(str(path), templates=self.templates)
                if data:
                    return data
            except Exception as e:  # pragma: no cover - optional dependency
                logging.warning("invoice2data error: %s", e)

        image = Image.open(image_path).convert("RGB")
        if self.use_donut:
            task_prompt = "<s_cord-v2>"
            decoder_input_ids = self.processor.tokenizer(
                task_prompt, add_special_tokens=False, return_tensors="pt"
            ).input_ids

            pixel_values = self.processor(image, return_tensors="pt").pixel_values
            outputs = self.model.generate(
                pixel_values.to(self.device),
                decoder_input_ids=decoder_input_ids.to(self.device),
                max_length=self.model.decoder.config.max_position_embeddings,
                pad_token_id=self.processor.tokenizer.pad_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
                use_cache=True,
                bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
            )

            sequence = self.processor.batch_decode(outputs.sequences)[0]
            sequence = (
                sequence.replace(self.processor.tokenizer.eos_token, "")
                .replace(self.processor.tokenizer.pad_token, "")
                .strip()
            )

            result = self._sequence_to_json(sequence)
            torch.cuda.empty_cache()
            return result
        else:
            text = pytesseract.image_to_string(image, lang="eng")
            return {"text": text.strip()}

    def _sequence_to_json(self, sequence: str) -> dict:
        try:
            return json.loads(self.processor.token2json(sequence))
        except Exception:
            logging.warning("token2json failed; returning raw output")
            return {"raw_output": sequence}


if __name__ == "__main__":
    parser = InvoiceParser()
    data = parser.parse_invoice("sample_invoice.png")
    print(json.dumps(data, indent=2, ensure_ascii=False))
