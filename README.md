diff --git a/README.md b/README.md
index 32ffb559105528da0bcd99dd356c9d63ebde69e7..e4007d6e3aea1b9209b814abd96c596b6e948bc0 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,98 @@
-# Matriks-ai-
-company
+# Matriks AI
+
+[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gaffam/matriks-ai/blob/main/colab_train.ipynb)
+
+Matriks AI sesli sorgulara yanit veren hafif bir saha asistanidir. Whisper.cpp ile
+ses kaydi yaziya cevrilir, fine tune edilmis Mistral modelinden cevap alinir ve
+Piper ile seslendirilir. Fatura goruntulerini Donut modeliyle isleyip JSON
+ciktisi uretme ve proforma hesabi yapma yetenekleri vardir.
+
+```
+Kullanici -> STT -> Intent -> LLM -> TTS -> Kullanici
+                |                  |
+                +---- Dokuman Arama +
+```
+Yerel model yetersiz kaldiginda sorgular `api_settings.base_url` ile belirtilen
+bulut sunucusuna gonderilebilir.
+
+## Gereksinimler
+- Python 3.10+
+- Linux veya WSL ortaminda calisan `pip`
+- GPU tavsiye edilir (CUDA 11.7+, >4GB) aksi halde fatura modelinde Tesseract
+  OCR kullanilir
+Dokuman arama icin basit bir vektor veritabani olusturulur ve LLM'e baglam saglanir.
+
+## Kurulum
+1. Depoyu klonlayin ve `setup.sh` calistirin:
+   ```bash
+   ./setup.sh
+   ```
+   Internet erisimi olmayan ortamlarda `pip install -r requirements.txt`
+   komutunu manuel calistirabilirsiniz.
+Datasetleri indirmek icin `src/data_loader.py` config.yaml'daki `datasets` bolumunu okur. `setup.sh` bunu otomatik olarak cagirir. Offline ortamlarda veri klasorlerini manuel ekleyin.
+2. `.env` dosyasini olusturmak icin `.env.example` dosyasini kopyalayin ve
+   SMTP, JWT gibi bilgileri doldurun.
+3. `models/finetuned-mistral.gguf` dosyasini ve egitim verilerini `data/`
+   klasorlerine yerlestirin.
+
+## Hızlı Başlangıç
+```bash
+python src/cli_app.py --mic                # mikrofondan soru sor
+python src/cli_app.py --parse-invoice f.png
+python src/cli_app.py --recommend Bursa fabrika
+python src/cli_app.py --spec ihale.txt
+```
+
+## Model Egitimi
+`docs/instruction_data.jsonl` dosyasini genisleterek egitimi
+`src/train_mistral_lora.py` ile Colab'da baslatabilirsiniz. Kolayca bir
+Colab baglantisi uretmek icin `src/colab_launcher.py` scriptini calistirin.
+Egitim sonucunda olusan `.safetensors` dosyasini `convert_to_gguf.sh`
+scriptiyle GGUF bicimine donusturun.
+
+## Paket Olusturma
+`create_package.sh` betigi `models/`, `data/`, `docs/` ve `src/` klasorlerini
+`proai_package.tar.gz` arsivine toplar. Bu arsivi diger sistemlere tasiyip
+`setup.sh` sonrasinda ayni sekilde kullanabilirsiniz.
+
+## Sunucu Modu
+`src/api_server.py` FastAPI tabanli bir sunucu saglar. Baslatmak icin
+```bash
+make run-api
+```
+`config.yaml` altindaki `api_settings` ile istemciler bu sunucuya baglanabilir.
+
+## Android
+
+Mobil saha kullanimi icin `mobil_kivy_app.py` dosyasinda Kivy tabanli cok basit
+bir arayuz bulunur. Uygulama bir *Konus* dugmesi ile mikrofondan kayit alir, LLM
+yanitini gosterir ve isterse seslendirebilir. Uygulamayi APK haline getirmek
+icin [Buildozer](https://github.com/kivy/buildozer) kullanilabilir:
+
+```bash
+pip install buildozer
+buildozer android debug
+```
+
+Olusan `bin/*.apk` dosyasi Android cihaza kurulabilir. Telefonun donanimi
+yetmiyorsa `config.yaml` altinda belirtilen `api_settings` araciligiyla sunucu
+moduna baglanilabilir.
+
+## Kanit AI Modulleri
+Bu paket altindaki `kanit_ai` modulunde, bakim log analizi ve sozlesme uretimi
+icin yardimci araclar bulunur.
+
+## Proje Tabanli Urun Secimi
+`product_selector.recommend_brand` fonksiyonu, proje konumu ve turune gore
+onerilen markayi dondurur. Ihale sartnamesindeki malzeme ve personel ihtiyaci
+`spec_reader.parse_spec` ile cikarilabilir.
+
+## Makefile
+Projeyi kolay calistirmak icin temel hedefler:
+
+```bash
+make setup   # kurulum
+make test    # testleri calistir
+make run-api # API sunucusunu baslat
+make package # arsiv olustur
+```
