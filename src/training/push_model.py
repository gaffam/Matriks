from huggingface_hub import HfApi
from pathlib import Path


def push_model(model_path: str, repo_id: str) -> None:
    api = HfApi()
    api.upload_file(
        path_or_fileobj=model_path,
        path_in_repo=Path(model_path).name,
        repo_id=repo_id,
        repo_type="model",
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload GGUF model to HF hub")
    parser.add_argument("model_path", help="Path to .gguf file")
    parser.add_argument("repo_id", help="Hugging Face repo id")
    args = parser.parse_args()
    push_model(args.model_path, args.repo_id)
