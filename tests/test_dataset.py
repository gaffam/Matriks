import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

pytest.importorskip('datasets')
from training.train_mistral_lora import build_text

def test_build_text_handles_output_and_response(tmp_path):
    data = [
        {'instruction': 'A', 'output': 'B'},
        {'instruction': 'C', 'response': 'D'},
    ]
    texts = [build_text(d) for d in data]
    assert texts[0].endswith('B')
    assert texts[1].endswith('D')


def test_dataset_has_examples():
    path = Path('docs/instruction_data.jsonl')
    assert path.exists()
    lines = path.read_text(encoding='utf-8').splitlines()
    assert len(lines) >= 10
