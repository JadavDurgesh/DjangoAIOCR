#!/bin/bash
set -e  # Exit on error

echo "Updating system packages..."
apt-get update && apt-get install -y tesseract-ocr libtesseract-dev libgl1

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r myproject/requirement.txt  # Adjust path if needed

echo "Downloading model from Google Drive..."
mkdir -p myproject/myapp
cd myproject/myapp
pip install gdown
gdown https://drive.google.com/uc?id=1UXU1FV6ZNuB0HOJDrledlOjdkRNxLMZv
cd ../..

echo "Running tests..."
cd myproject
python manage.py runserver
