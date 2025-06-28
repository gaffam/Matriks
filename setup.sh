#!/bin/bash
pip install -r requirements.txt

# optional dataset download
if [ -f "config.yaml" ]; then
  python src/data_loader.py --config config.yaml
fi

echo "Kurulum tamamlandi!"
