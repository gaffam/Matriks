#!/bin/bash
# convert_to_gguf.sh
# Bu script, LoRA ile egitilmis modeli GGUF formatina donusturur

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Kullanim: $0 <pytorch_model.bin yolu> <gguf cikti dosya yolu> [QTYPE]" >&2
  exit 1
fi

MODEL_BIN_PATH="$1"
GGUF_OUTPUT_PATH="$2"
QUANT="${3:-Q4_K}"

# 1. llama.cpp'yi klonla (yoksa)
if [ ! -d "llama.cpp" ]; then
  git clone https://github.com/ggerganov/llama.cpp.git
fi

# 2. convert.py varsa calistir
cd llama.cpp || exit 1

if [ ! -f "convert.py" ]; then
  echo "convert.py bulunamadi!" >&2
  exit 1
fi

# 3. Donusturme
python3 convert.py "$MODEL_BIN_PATH" --outfile "$GGUF_OUTPUT_PATH" --quantize "$QUANT"

cd ..
echo "GGUF dosyasi olusturuldu: $GGUF_OUTPUT_PATH"
