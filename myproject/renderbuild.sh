#!/bin/bash
set -e  # Exit on error

echo "Updating system packages..."
apt-get update && apt-get install -y tesseract-ocr libtesseract-dev libgl1

echo "Installing Python dependencies..."
#cd myproject
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Downloading model from Google Drive..."
cd myapp
pip install gdown
gdown https://drive.google.com/uc?id=1UXU1FV6ZNuB0HOJDrledlOjdkRNxLMZv
cd ..

echo "Running tests..."
python manage.py test
