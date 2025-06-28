"""Interface to a local Llama.cpp model (e.g. Mistral 7B GGUF)."""

from pathlib import Path
from typing import Optional
import logging


class LLMError(Exception):
    """Custom error for LLM related problems."""


from doc_search import search as search_docs

from config import load_config
from prompt_cache import PromptCache

from llama_cpp import Llama
import os

CFG = load_config()
DEFAULT_MODEL_PATH = CFG.get("models", {}).get("llm", "models/finetuned-mistral.gguf")

# Prompt cache backed by SQLite
_PROMPT_CACHE: dict[str, str] = {}
_cache_db = PromptCache()


class LLMClient:
    """A thin wrapper around ``llama_cpp.Llama`` for question answering."""

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH, n_ctx: int = 2048):
        self.model_path = Path(model_path)
        self.n_ctx = n_ctx
        n_threads = int(os.getenv("LLAMA_THREADS", "4"))
        self._llm = Llama(model_path=str(self.model_path), n_ctx=n_ctx, n_threads=n_threads)

    def _build_prompt(self, question: str) -> str:
        examples = (
            "Soru: Kod 135 ne demek?\nCevap: Yangin butonundan gelen hatali surekli sinyal.\n\n"
            "Soru: Kod 227 ne anlama gelir?\nCevap: Alarm paneli ile iletisim kaybi.\n\n"
        )
        return examples + f"Soru: {question}\nCevap:"

    def ask(self, prompt: str, max_tokens: int = 256) -> str:
        cached = _PROMPT_CACHE.get(prompt) or _cache_db.get(prompt)
        if cached:
            _PROMPT_CACHE[prompt] = cached
            return cached

        context = search_docs(prompt)
        base_prompt = self._build_prompt(prompt)
        if context:
            full_prompt = f"Bilgi: {context}\n\n" + base_prompt
        else:
            full_prompt = base_prompt
        try:
            response = self._llm(full_prompt, max_tokens=max_tokens, echo=False)
            answer = response["choices"][0]["text"].strip()
        except Exception as exc:
            logging.error("LLM failed: %s", exc, exc_info=True)
            raise LLMError(str(exc)) from exc
        _PROMPT_CACHE[prompt] = answer
        _cache_db.set(prompt, answer)
        return answer


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Ask the local LLM")
    parser.add_argument("prompt", help="Question to ask")
    parser.add_argument("--model", required=True, help="Path to GGUF model")
    args = parser.parse_args()

    client = LLMClient(args.model)
    print(client.ask(args.prompt))


if __name__ == "__main__":
    main()
