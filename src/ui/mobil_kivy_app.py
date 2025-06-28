"""Kivy tabanli basit GUI.

Ses dosyasi secip 'Calistir' dugmesine basildiginda
STT, LLM ve TTS akisi tetiklenir. Android icin ornek arayuzdur."""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.cache import Cache
import datetime
import threading

from utils.config import load_config

from speech.speech_client import transcribe_mic
from assistant.ask_llm import LLMClient
from assistant.proforma_engine import create_quote
from speech.voice_response import speak


CFG = load_config()
Cache.register('llm_responses', limit=100)
store = JsonStore('offline_data.json')


class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        Builder.load_file("mobil_kivy_app.kv")
        super().__init__(orientation="vertical", **kwargs)
        self.label = self.ids.output
        self.llm = None
        self.last_quote = None

    def run_query(self, instance):
        threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        if not self.llm:
            model_path = CFG.get("models", {}).get("llm", "models/finetuned-mistral.gguf")
            self.llm = LLMClient(model_path)
        lang = CFG.get("language")
        text = transcribe_mic(lang=lang or "tr")
        if not lang:
            from utils.lang_detect import detect_lang
            lang = detect_lang(text)
        result = self.handle(text)

        def update(dt):
            self.label.text = result

        Clock.schedule_once(update)
        speak(result, lang=lang)
        store.put('last_query', text=text, answer=result)

    def handle(self, text: str) -> str:
        if text.lower().startswith("proforma"):
            req = text[len("proforma"):].strip()
            q = create_quote(req)
            self.last_quote = q
            items = ", ".join(f"{it['adet']} {it['urun']}" for it in q['kalemler'])
            return f"{items} toplam {q['toplam']} TL"
        self.last_quote = None
        answer = self.llm.ask(text)
        Cache.append('llm_responses', (text, answer))
        return answer

    def send_pdf(self, instance):
        if not self.last_quote:
            self.label.text = "Once proforma olusturun"
            return
        pdf_path = "teklif.pdf"
        from assistant.proforma_engine import quote_to_pdf
        from utils.send_email import send_email

        quote_to_pdf(self.last_quote, pdf_path)
        to_addr = CFG.get("email", {}).get("default_to")
        if to_addr:
            send_email(to_addr, "Proforma", "Ekte teklif", pdf_path)
            self.label.text = f"PDF gonderildi: {to_addr}"
        else:
            self.label.text = "Email ayari yok"

    def send_feedback(self, good: bool):
        if not store.exists('last_query'):
            self.label.text = "Once soru sorun"
            return
        data = store.get('last_query')
        key = 'fb_' + datetime.datetime.now().isoformat()
        store.put(key, text=data['text'], answer=data['answer'], good=good)
        self.label.text = "Geri bildirim icin tesekkurler"


class ProAIApp(App):
    def build(self):
        return MainWidget()


if __name__ == "__main__":
    ProAIApp().run()
