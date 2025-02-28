import os
import json
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader  # For PDF text extraction
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ExtractedData
from .utils import detect_text  # Your function to process images/text into structured data
from pdf2image import convert_from_path
from django.shortcuts import render
import pandas as pd  # For Excel/CSV generation

class UploadExtractFileView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if 'files' not in request.FILES:
            return JsonResponse({'error': 'No files provided'}, status=400)

        files = request.FILES.getlist('files')  # Get multiple files
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        extracted_results = []
        combined_df = pd.DataFrame()  # Combined DataFrame for all files

        try:
            for file in files:
                file_path = os.path.join(upload_dir, file.name)

                # Save file to disk
                with open(file_path, "wb+") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                extracted_data = None  # To store extracted data
                image_urls = []       # To store info on converted images

                # Process images directly
                if file.content_type.startswith('image'):
                    extracted_data = detect_text(file_path)

                # Process PDFs: extract text and convert pages to images
                elif file.content_type == 'application/pdf':
                    text = ""
                    structured_data = []

                    # Extract raw text from PDF using PyPDF2
                    with open(file_path, "rb") as pdf_file:
                        reader = PdfReader(pdf_file)
                        for page in reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"

                    # Convert PDF pages to images using pdf2image
                    images = convert_from_path(file_path)
                    for i, img in enumerate(images):
                        image_filename = f"{file.name}_page_{i+1}.png"
                        image_path = os.path.join(upload_dir, image_filename)
                        img.save(image_path, "PNG")  # Save page as PNG

                        # Run OCR and any additional processing on the image
                        detected_text = detect_text(image_path)

                        # Append the detected structured data from this page
                        structured_data.extend(detected_text)

                        image_urls.append({
                            "image_url": f"{settings.MEDIA_URL}uploads/{image_filename}",
                            "ocr_text": detected_text
                        })

                    # For PDFs, you can store both the raw text and the structured data
                    '''extracted_data = {
                        "pdf_text": text,
                        "structured_data": structured_data,
                        "pdf_images": image_urls
                    }'''
                    extracted_data = structured_data

                # Save the extracted data to the database. If you updated your model to use a FileField called "file", use that.
                ExtractedData.objects.create(
                    image=file,  # Or use 'file=file' if you've updated your model
                    extracted_json=extracted_data
                )

                # Save the extracted data as a JSON file
                json_filename = os.path.join(upload_dir, f"{file.name}.json")
                with open(json_filename, "w") as json_file:
                    json.dump(extracted_data, json_file, indent=4)

                # Create a DataFrame from the structured data.
                # For images, assume extracted_data is already a list of dictionaries.
                # For PDFs, use the "structured_data" key.
                '''if file.content_type == 'application/pdf' and isinstance(extracted_data, dict):
                    data = extracted_data.get("structured_data", [])
                else:
                    data = extracted_data'''

                df = pd.DataFrame(extracted_data)

                # Save individual Excel and CSV files for this file
                excel_filename = f"{file.name}.xlsx"
                excel_path = os.path.join(upload_dir, excel_filename)
                df.to_excel(excel_path, index=False)

                csv_filename = f"{file.name}.csv"
                csv_path = os.path.join(upload_dir, csv_filename)
                df.to_csv(csv_path, index=False)

                # Append current file's DataFrame to the combined DataFrame
                combined_df = pd.concat([combined_df, df], ignore_index=True)

                extracted_results.append({
                    'file_url': f"{settings.MEDIA_URL}uploads/{file.name}",
                    'json_file_url': f"{settings.MEDIA_URL}uploads/{file.name}.json",
                    'excel_file_url': f"{settings.MEDIA_URL}uploads/{excel_filename}",
                    'csv_file_url': f"{settings.MEDIA_URL}uploads/{csv_filename}",
                    'extracted_json': extracted_data
                })

            # Save combined DataFrame as Excel and CSV files
            combined_excel_filename = "combined.xlsx"
            combined_excel_path = os.path.join(upload_dir, combined_excel_filename)
            combined_df.to_excel(combined_excel_path, index=False)

            combined_csv_filename = "combined.csv"
            combined_csv_path = os.path.join(upload_dir, combined_csv_filename)
            combined_df.to_csv(combined_csv_path, index=False)

            return JsonResponse({
                'results': extracted_results,
                'combined_excel_file_url': f"{settings.MEDIA_URL}uploads/{combined_excel_filename}",
                'combined_csv_file_url': f"{settings.MEDIA_URL}uploads/{combined_csv_filename}"
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        
'''class GetExtractedDataView(APIView):
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

        return JsonResponse({"extracted_results": data_list}, safe=False, status=200)'''

class GetExtractedDataView(APIView):
    def get(self, request, *args, **kwargs):
        extracted_data_qs = ExtractedData.objects.all()

        if not extracted_data_qs.exists():
            return JsonResponse({"message": "No extracted data found"}, status=404)

        data_list = []
        combined_dfs = []  # List to hold all DataFrames for the combined file

        # Create a directory to store generated Excel/CSV files if it doesn't exist
        generated_dir = os.path.join(settings.MEDIA_ROOT, 'generated_files')
        os.makedirs(generated_dir, exist_ok=True)

        for data in extracted_data_qs:
            # Build the absolute URL for the file field (assumed to be stored in the 'image' field)
            image_url = request.build_absolute_uri(data.image.url)

            # Get the extracted JSON from the database; assume it is a list of dictionaries.
            extracted = data.extracted_json
            if not isinstance(extracted, list):
                extracted = [extracted]

            # Create a DataFrame from the extracted data
            df = pd.DataFrame(extracted)
            combined_dfs.append(df)

            # Generate filenames based on the record's ID
            base_filename = f"extracted_{data.id}"
            excel_filename = f"{base_filename}.xlsx"
            csv_filename = f"{base_filename}.csv"
            excel_path = os.path.join(generated_dir, excel_filename)
            csv_path = os.path.join(generated_dir, csv_filename)

            # Save the DataFrame as Excel and CSV files
            df.to_excel(excel_path, index=False)
            df.to_csv(csv_path, index=False)

            # Build URLs for the generated files
            individual_excel_url = request.build_absolute_uri(
                os.path.join(settings.MEDIA_URL, 'generated_files', excel_filename)
            )
            individual_csv_url = request.build_absolute_uri(
                os.path.join(settings.MEDIA_URL, 'generated_files', csv_filename)
            )

            data_list.append({
                "image_url": image_url,
                "extracted_data": data.extracted_json,
                "uploaded_at": data.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                "individual_excel_url": individual_excel_url,
                "individual_csv_url": individual_csv_url
            })

        # Create combined DataFrame and save as combined Excel and CSV files
        if combined_dfs:
            combined_df = pd.concat(combined_dfs, ignore_index=True)
            combined_excel_filename = "combined_extracted.xlsx"
            combined_csv_filename = "combined_extracted.csv"
            combined_excel_path = os.path.join(generated_dir, combined_excel_filename)
            combined_csv_path = os.path.join(generated_dir, combined_csv_filename)
            combined_df.to_excel(combined_excel_path, index=False)
            combined_df.to_csv(combined_csv_path, index=False)
            combined_excel_url = request.build_absolute_uri(
                os.path.join(settings.MEDIA_URL, 'generated_files', combined_excel_filename)
            )
            combined_csv_url = request.build_absolute_uri(
                os.path.join(settings.MEDIA_URL, 'generated_files', combined_csv_filename)
            )
        else:
            combined_excel_url = ""
            combined_csv_url = ""

        return JsonResponse({
            "extracted_results": data_list,
            "combined_excel_file_url": combined_excel_url,
            "combined_csv_file_url": combined_csv_url
        }, safe=False, status=200)
    
def index(request):
    return render(request,"upload.html")
def show_extracted_data(request):
    extracted_data_qs = ExtractedData.objects.all()

    if not extracted_data_qs.exists():
        return render(request, "show_extracted.html", {"message": "No extracted data found."})

    data_list = []
    combined_dfs = []  # List to hold all DataFrames for the combined file

    # Directory for generated Excel/CSV files
    generated_dir = os.path.join(settings.MEDIA_ROOT, 'generated_files')
    os.makedirs(generated_dir, exist_ok=True)

    for data in extracted_data_qs:
        # Use relative URL by simply concatenating settings.MEDIA_URL (which should start with a slash)
        image_url = settings.MEDIA_URL + data.image.url.split(settings.MEDIA_URL)[-1]
        
        # Get the extracted JSON from the database; assume it is a list of dictionaries.
        extracted = data.extracted_json
        if not isinstance(extracted, list):
            extracted = [extracted]

        # Create a DataFrame from the extracted data
        df = pd.DataFrame(extracted)
        combined_dfs.append(df)

        # Generate filenames based on the record's ID
        base_filename = f"extracted_{data.id}"
        excel_filename = f"{base_filename}.xlsx"
        csv_filename = f"{base_filename}.csv"
        excel_path = os.path.join(generated_dir, excel_filename)
        csv_path = os.path.join(generated_dir, csv_filename)

        # Save the DataFrame as Excel and CSV files
        df.to_excel(excel_path, index=False)
        df.to_csv(csv_path, index=False)

        # Build relative URLs for the generated files
        individual_excel_url = os.path.join(settings.MEDIA_URL, 'generated_files', excel_filename)
        individual_csv_url = os.path.join(settings.MEDIA_URL, 'generated_files', csv_filename)

        data_list.append({
            "image_url": image_url,
            "extracted_data": data.extracted_json,
            "uploaded_at": data.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
            "individual_excel_url": individual_excel_url,
            "individual_csv_url": individual_csv_url
        })

    # Create combined DataFrame and save as combined Excel and CSV files
    if combined_dfs:
        combined_df = pd.concat(combined_dfs, ignore_index=True)
        combined_excel_filename = "combined_extracted.xlsx"
        combined_csv_filename = "combined_extracted.csv"
        combined_excel_path = os.path.join(generated_dir, combined_excel_filename)
        combined_csv_path = os.path.join(generated_dir, combined_csv_filename)
        combined_df.to_excel(combined_excel_path, index=False)
        combined_df.to_csv(combined_csv_path, index=False)
        combined_excel_url = os.path.join(settings.MEDIA_URL, 'generated_files', combined_excel_filename)
        combined_csv_url = os.path.join(settings.MEDIA_URL, 'generated_files', combined_csv_filename)
    else:
        combined_excel_url = ""
        combined_csv_url = ""

    context = {
        "extracted_results": data_list,
        "combined_excel_file_url": combined_excel_url,
        "combined_csv_file_url": combined_csv_url
    }
    return render(request, "show_extracted.html", context)

