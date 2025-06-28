"""Minimal command line assistant demo."""

import argparse
import json
import logging
import os
from pathlib import Path

from config import load_config

from speech_client import transcribe, transcribe_mic
from ask_llm import LLMClient
from api_client import ask_cloud
from voice_response import speak
from proforma_engine import create_quote, quote_to_pdf
from invoice_parser import InvoiceParser


CFG = load_config()
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(filename="logs/app.log", level=logging.INFO, format="%(asctime)s %(message)s")
dsn = os.environ.get("SENTRY_DSN")
if dsn:
    try:
        import sentry_sdk

        sentry_sdk.init(dsn=dsn)
    except Exception:
        logging.warning("Failed to init Sentry")
KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent / CFG.get(
    "paths", {}
).get("fault_db", "fault_knowledge.json")


def load_fault_db():
    if not KNOWLEDGE_PATH.exists():
        return {}
    with KNOWLEDGE_PATH.open("r", encoding="utf-8") as fh:
        return {entry["code"]: entry["description"] for entry in json.load(fh)}


def handle_query(query: str, llm: LLMClient, faults: dict) -> tuple[str, dict | None]:
    for code, desc in faults.items():
        if code in query:
            return desc, None
    if query.lower().startswith("proforma"):
        request = query[len("proforma"):].strip()
        try:
            quote = create_quote(request)
        except ValueError as exc:
            return str(exc), None
        items = ", ".join(f"{it['adet']} {it['urun']}" for it in quote['kalemler'])
        text = f"{items} toplam {quote['toplam']} TL"
        return text, quote
    return llm.ask(query), None


def get_answer(query: str, llm: LLMClient, faults: dict) -> tuple[str, dict | None]:
    if query.startswith("derin analiz") or len(query) > 200:
        print("\u2601\ufe0f Karma\u015f\u0131k sorgu i\u00e7in bulut API kullan\u0131l\u0131yor...")
        try:
            return ask_cloud(query), None
        except Exception as exc:
            print(f"Bulut API hatas\u0131: {exc}. Yerel model kullan\u0131l\u0131yor...")
    return handle_query(query, llm, faults)


def main():
    parser = argparse.ArgumentParser(description="ProAIforma Saha Asistan\u0131")
    parser.add_argument("audio", nargs="?", help="Path to recorded query")
    parser.add_argument("--mic", action="store_true", help="Kayd\u0131 mikrofondan al")
    parser.add_argument(
        "--model",
        default=CFG.get("models", {}).get("llm", "models/finetuned-mistral.gguf"),
        help="Path to fine-tuned GGUF model",
    )
    parser.add_argument("--voice", default=None, help="TTS voice name")
    parser.add_argument("--lang", default=None, help="Dil kodu (STT/TTS)")
    parser.add_argument("--pdf", help="Yaniti PDF olarak kaydet")
    parser.add_argument("--email", help="PDF dosyasini bu adrese gonder")
    parser.add_argument(
        "--parse-invoice",
        help="Resim veya PDF faturayi isleyip JSON cikti verir",
    )
    parser.add_argument(
        "--recommend",
        nargs=2,
        metavar=("SEHIR", "TIP"),
        help="Proje yeri ve turune gore marka oner",
    )
    parser.add_argument(
        "--spec",
        help="Ihale sartnamesini okuyup malzeme/personel listesi cikartir",
    )
    parser.add_argument(
        "--templates",
        default=CFG.get("paths", {}).get("invoice_templates"),
        help="invoice2data sablon klasoru (PDF icin)",
    )
    args = parser.parse_args()

    faults = load_fault_db()
    llm = LLMClient(args.model)

    if args.parse_invoice:
        print(f"'{args.parse_invoice}' dosyasi isleniyor...")
        parser_cls = InvoiceParser(templates_dir=args.templates)
        data = parser_cls.parse_invoice(args.parse_invoice)
        print("\n--- Cikarilan Fatura Bilgileri ---")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("---------------------------------")
        return

    if args.recommend:
        from product_selector import recommend_brand

        brand = recommend_brand({"location": args.recommend[0], "type": args.recommend[1]})
        print(f"Onerilen marka: {brand}")
        return

    if args.spec:
        from spec_reader import parse_spec

        reqs = parse_spec(args.spec)
        print(json.dumps(reqs, indent=2, ensure_ascii=False))
        return

    if args.mic or not args.audio:
        text = transcribe_mic(lang=args.lang)
    else:
        text = transcribe(args.audio, lang=args.lang)

    from lang_detect import detect_lang
    detected = detect_lang(text)
    if not args.lang:
        args.lang = detected
    logging.info("Query: %s", text)
    if 'sentry_sdk' in globals():
        try:
            sentry_sdk.add_breadcrumb(category="query", message=text)
        except Exception:
            pass
    answer, quote = get_answer(text, llm, faults)
    print(answer)
    logging.info("Answer: %s", answer)
    if args.pdf and quote:
        quote_to_pdf(quote, args.pdf)
        print(f"PDF kaydedildi: {args.pdf}")
        if args.email:
            from send_email import send_email

            send_email(
                args.email,
                "Proforma Teklif",
                "Istediginiz teklif ektedir",
                args.pdf,
            )
            print("PDF e-posta ile gonderildi")
    speak(answer, voice=args.voice, lang=args.lang)

    fb = input("Yanit faydali oldu mu? [y/n]: ").strip().lower()
    Path("logs").mkdir(exist_ok=True)
    with open("logs/feedback.csv", "a", encoding="utf-8") as fb_file:
        fb_file.write(f"{text}\t{answer}\t{fb}\n")


if __name__ == "__main__":
    main()
