
import os
import json
import pytesseract
from PIL import Image
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ExtractedData
from .utils import detect_text
from django.shortcuts import render

class UploadExtractImageView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image file provided'}, status=400)

        image_file = request.FILES['image']
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        image_path = os.path.join(upload_dir, image_file.name)

        try:
            with open(image_path, "wb+") as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            # Extract text using Faster R-CNN & OCR
            extracted_data = detect_text(image_path)

            # Save to database
            extracted_instance = ExtractedData.objects.create(
                image=image_file, extracted_json=extracted_data
            )

            # Save extracted data as JSON file
            json_filename = os.path.join(upload_dir, "extracted_data.json")
            with open(json_filename, "w") as json_file:
                json.dump(extracted_data, json_file, indent=4)

            return JsonResponse({
                'message': 'File uploaded and processed successfully',
                'file_url': f"{settings.MEDIA_URL}uploads/{image_file.name}",
                'json_file_url': f"{settings.MEDIA_URL}uploads/extracted_data.json",
                'extracted_json': extracted_data
            }, status=201)

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
