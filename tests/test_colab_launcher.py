from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from colab_launcher import generate_colab_url


def test_generate_colab_url():
    url = generate_colab_url("https://github.com/org/repo")
    assert "colab.research.google.com" in url
    assert "repo/blob/main/colab_train.ipynb" in url
