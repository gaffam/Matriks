import urllib.parse
from pathlib import Path


def generate_colab_url(repo_url: str, data_path: str = "data/instruction_data.jsonl") -> str:
    """Create a Colab URL for running the training notebook."""
    base_colab_url = "https://colab.research.google.com/github/"
    repo_path = urllib.parse.urlparse(repo_url).path.strip("/")
    notebook_path = f"{repo_path}/blob/main/colab_train.ipynb"
    return f"{base_colab_url}{notebook_path}?file={data_path}"


def save_colab_launcher(repo_url: str, output_path: str = "launch_colab.html") -> None:
    """Write an HTML file with an 'Open in Colab' badge linking to the notebook."""
    url = generate_colab_url(repo_url)
    html = f"""
    <html>
    <body>
        <a href=\"{url}\" target=\"_blank\">
            <img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open in Colab\"/>
        </a>
    </body>
    </html>
    """
    Path(output_path).write_text(html.strip(), encoding="utf-8")
    print(f"Colab link saved to {output_path}")


if __name__ == "__main__":
    save_colab_launcher("https://github.com/gaffam/matriks-ai")
