#!/bin/bash
set -e  # Exit on error

echo "Updating system packages..."
apt-get clean && apt-get update --allow-releaseinfo-change && apt-get install -y --no-install-recommends tesseract-ocr libtesseract-dev libgl1

echo "Installing Python dependencies..."
cd myproject

python -m pip install --upgrade pip gdown django djangorestframework pillow torchvision opencv-python pytesseract

echo "Downloading model from Google Drive..."
cd myapp
ls
gdown https://drive.google.com/uc?id=1UXU1FV6ZNuB0HOJDrledlOjdkRNxLMZv
cd ..
ls
echo "Running tests..."
python manage.py test
