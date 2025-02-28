import os
import json
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader  # Import for PDF processing
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ExtractedData
from .utils import detect_text
from pdf2image import convert_from_path
from django.shortcuts import render

class UploadExtractFileView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if 'files' not in request.FILES:
            return JsonResponse({'error': 'No files provided'}, status=400)

        files = request.FILES.getlist('files')  # Get multiple files
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        extracted_results = []

        try:
            for file in files:
                file_path = os.path.join(upload_dir, file.name)

                # Save file
                with open(file_path, "wb+") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                extracted_data = None  # Store extracted data
                image_urls = []  # To store info on converted images

                # Process images directly
                if file.content_type.startswith('image'):
                    extracted_data = detect_text(file_path)

                # Process PDFs: extract text and convert pages to images
                elif file.content_type == 'application/pdf':
                    text = ""
                    structured_data = []

                    # Extract text from PDF
                    with open(file_path, "rb") as pdf_file:
                        reader = PdfReader(pdf_file)
                        for page in reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"

                    # Convert PDF pages to images
                    images = convert_from_path(file_path)
                    for i, img in enumerate(images):
                        image_filename = f"{file.name}_page_{i+1}.png"
                        image_path = os.path.join(upload_dir, image_filename)
                        img.save(image_path, "PNG")  # Save as PNG

                        # Run OCR (and any additional processing) on the image
                        detected_text = detect_text(image_path)

                        # Append the detected structured data from this page
                        structured_data.extend(detected_text)

                        image_urls.append({
                            "image_url": f"{settings.MEDIA_URL}uploads/{image_filename}",
                            "ocr_text": detected_text
                        })

                    extracted_data = {
                        #"structured_data": structured_data,
                        "pdf_images": image_urls
                    }

                # Save the results to the database
                extracted_instance = ExtractedData.objects.create(
                    image=file, extracted_json=extracted_data
                )

                # Save the extracted data as a JSON file
                json_filename = os.path.join(upload_dir, f"{file.name}.json")
                with open(json_filename, "w") as json_file:
                    json.dump(extracted_data, json_file, indent=4)

                extracted_results.append({
                    'message': 'File uploaded and processed successfully',
                    'file_url': f"{settings.MEDIA_URL}uploads/{file.name}",
                    'json_file_url': f"{settings.MEDIA_URL}uploads/{file.name}.json",
                    'extracted_json': extracted_data
                })

            return JsonResponse({'results': extracted_results}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class GetExtractedDataView(APIView):
    def get(self, request, *args, **kwargs):
        extracted_data = ExtractedData.objects.all()

        if not extracted_data.exists():
            return JsonResponse({"message": "No extracted data found"}, status=404)

        data_list = []
        for data in extracted_data:
            data_list.append({
                "image_url": request.build_absolute_uri(data.image.url),  # Full image URL
                "extracted_data": data.extracted_json,
                "uploaded_at": data.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),  # Friendly date format
            })

        return JsonResponse({"extracted_results": data_list}, safe=False, status=200)
    
def index(request):
    return render(request,"upload.html")
