import argparse
import os
import sys
import logging
from pathlib import Path
import yaml
import pandas as pd

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    KAGGLE_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    KAGGLE_AVAILABLE = False

try:
    from datasets import load_dataset as hf_load_dataset
    HF_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    HF_AVAILABLE = False


def load_github_csv(raw_url: str, output_path: str) -> None:
    """Download a CSV from a raw GitHub URL."""
    try:
        df = pd.read_csv(raw_url)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logging.info("GitHub CSV saved to %s", output_path)
    except Exception as e:  # pragma: no cover - network issues
        logging.warning("Failed to fetch GitHub CSV: %s", e)


def download_kaggle_dataset(name: str, download_path: str) -> None:
    """Download a dataset from Kaggle."""
    if not KAGGLE_AVAILABLE:
        logging.warning("Kaggle API not installed")
        return
    api = KaggleApi()
    api.authenticate()
    Path(download_path).mkdir(parents=True, exist_ok=True)
    api.dataset_download_files(name, path=download_path, unzip=True)
    logging.info("Kaggle dataset %s downloaded to %s", name, download_path)


def download_hf_dataset(name: str, download_path: str) -> None:
    """Download a dataset from the Hugging Face Hub."""
    if not HF_AVAILABLE:
        logging.warning("datasets package not installed")
        return
    logging.info("Downloading %s from HF Hub", name)
    ds = hf_load_dataset(name)
    Path(download_path).mkdir(parents=True, exist_ok=True)
    ds.save_to_disk(download_path)
    logging.info("Hugging Face dataset saved to %s", download_path)


def load_from_config(config_path: str) -> None:
    """Load datasets defined in a YAML config."""
    data = yaml.safe_load(Path(config_path).read_text())
    sets = data.get('datasets', {})
    for src in sets.get('github_sources', []):
        load_github_csv(src['url'], src['output_path'])
    for src in sets.get('kaggle_sources', []):
        download_kaggle_dataset(src['name'], src['download_path'])
    for src in sets.get('hf_sources', []):
        download_hf_dataset(src['name'], src['download_path'])


def main() -> None:
    parser = argparse.ArgumentParser(description="Dataset downloader")
    parser.add_argument('--github', help='Raw GitHub CSV URL')
    parser.add_argument('--kaggle', help='Kaggle dataset name')
    parser.add_argument('--hf', help='HuggingFace dataset name')
    parser.add_argument('--output', help='Output path')
    parser.add_argument('--config', help='YAML config with multiple datasets')
    args = parser.parse_args()

    if args.config:
        load_from_config(args.config)
        return

    if args.github and args.output:
        load_github_csv(args.github, args.output)
    elif args.kaggle and args.output:
        download_kaggle_dataset(args.kaggle, args.output)
    elif args.hf and args.output:
        download_hf_dataset(args.hf, args.output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
