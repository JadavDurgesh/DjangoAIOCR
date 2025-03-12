import os
import json

#from PIL import Image
from PyPDF2 import PdfReader  # For PDF text extraction
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from .models import *
from .utils import detect_text  # Your function to process images/text into structured data
#from pdf2image import convert_from_path
import fitz  # PyMuPDF: pip install pymupdf
from django.shortcuts import render,get_object_or_404,redirect
import pandas as pd  # For Excel/CSV generation
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
import random

def logout(request):
    request.session.flush()
    return redirect('login')

def login(request):
    # If user is already logged in, redirect to index
    if request.session.get('user_id'):
        return redirect('index')

    if request.method == 'POST':
        email = request.POST.get('email', "").strip()
        password = request.POST.get('password', "").strip()
        keep_logged_in = request.POST.get('selector')  # Checkbox value

        try:
            user = Users.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id

                # If "Keep me logged in" is checked, extend session expiry
                if keep_logged_in:
                    request.session.set_expiry(60 * 60 * 24 * 365)  # 1 year session expiry
                else:
                    request.session.set_expiry(0)  # Default session expiry (browser session)

                return redirect('index')
            else:
                response_message = "Invalid Email or Password"
        except Users.DoesNotExist:
            response_message = "Invalid Email or Password"

        return render(request, 'login.html', {'response': response_message})

    return render(request, 'login.html', {'response': ""})


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', "").strip()
        otp = random.randint(1111, 9999)
        try:
            user = Users.objects.get(email=email)
            user.otp = otp
            user.save()  # Save the OTP in the database
            request.session['reset_email'] = email
            # Send email
            send_mail('Reset Password ','Your OTP is: '+str(user.otp),'shivam2552003@gmail.com',[email])

            # Redirect to change_password with email in session
            
            return redirect('change_password')

        except Users.DoesNotExist:
            response = "Invalid Email"
            return render(request, 'forgot-password.html', {'response': response})
        except Exception as e:
            response = str(e)
            return render(request, 'forgot-password.html', {'response': response})

    return render(request, 'forgot-password.html')

def change_password(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')  # Redirect if no email in session

    if request.method == 'POST':
        otp = request.POST.get('otp', "").strip()
        new_password = request.POST.get('new_password', "").strip()
        try:
            user = Users.objects.get(email=email)
            if str(user.otp) == otp and user.otp != 0:  # Ensure OTP is valid and non-zero
                user.password = make_password(new_password)
                user.otp = 0  # Reset OTP to avoid reuse
                user.save()
                # Clear session email after password reset
                del request.session['reset_email']
                return redirect('login')
            else:
                return render(request, 'change-password.html', {'response': 'Invalid OTP.'})
        except Users.DoesNotExist:
            return render(request, 'change-password.html', {'response': 'Invalid User.'})

    return render(request, 'change-password.html')

def register(request):
    if request.method == 'POST':
        # Extract form data
        email = request.POST.get('email', "").strip()
        first_name = request.POST.get('first_name', "").strip()
        last_name = request.POST.get('last_name', "").strip()
        phone_number = request.POST.get('phone_number', "").strip()
        password = request.POST.get('password', "").strip()

        # Check for existing email or phone number
        if Users.objects.filter(email=email).exists():
            response = "Email already exists"
            return render(request, 'register.html', {'response': response})
        if Users.objects.filter(phone_number=phone_number).exists():
            response = "Phone number already exists"
            return render(request, 'register.html', {'response': response})

        # Hash the password
        hashed_password = make_password(password)

        # Create new user
        Users.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=hashed_password
        )

        # Redirect to login page with success message
        return redirect('login')

    return render(request, 'register.html')

def my_account(request):
    uid = request.session.get('user_id')
    if not uid:
        return redirect('login')
    user=get_object_or_404(Users, id=uid)
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', "").strip()
        user.last_name = request.POST.get('last_name', "").strip()
        user.phone_number = request.POST.get('phone_number', "").strip()
        user.password = make_password(request.POST.get('password', "").strip())
        user.save()
        return redirect('my_account')
    return render(request,'my_account.html',{'user':user})

def delete_account(request):
    uid = request.session.get('user_id')  # Get logged-in user ID

    if not uid:
        return redirect('login')  # Redirect if user is not logged in

    user = get_object_or_404(Users, id=uid)  # Get user object

    if request.method == 'POST':
        password = request.POST.get('password', "").strip()  # Get entered password

        # Verify password before deleting account
        if check_password(password, user.password):  
            user.delete()  # Delete user account
            request.session.flush()  # Clear session
            return redirect('login')  # Redirect to login page after deletion
        else:
            return render(request, 'delete_account.html', {'error': 'Incorrect password'})

    return render(request, 'delete_account.html',{'error': ''})


def company_create(request):
    uid = request.session.get('user_id')
    if not uid:
        return redirect('login')
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        company_email = request.POST.get('company_email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        company_pan = request.POST.get('company_pan')
        company_gst = request.POST.get('company_gst')
        
        # Create and save a new Company instance
        company = Company.objects.create(
            company_name=company_name,
            company_email=company_email,
            password=password,  # For production, hash the password!
            phone=phone,
            address=address,
            company_pan=company_pan,
            company_gst=company_gst
        )
        # Redirect or show a success message
        return HttpResponse("Company registered successfully!")
    return render(request, "company_form.html")

def company_list(request):
    uid = request.session.get('user_id')
    if not uid:
        return redirect('login')
    companies = Company.objects.all()
    return render(request, "company_list.html", {"companies": companies})

def company_details(request, company_id):
    uid = request.session.get('user_id')
    if not uid:
        return redirect('login')
    company = get_object_or_404(Company, id=company_id)
    # Assuming the related CompanyDetails are linked via a related_name called 'details'
    details = company.company_details.all()  
    return render(request, "company_details.html", {"company": company, "details": details})

def UploadExtractFileView(request):
    uid = request.session.get('user_id')
    if not uid:
        return redirect('login')
    if request.method == 'POST':
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
                    # Convert PDF pages to images using PyMuPDF (no Poppler needed)
                    doc = fitz.open(file_path)
                    zoom_factor = 3  # Increase resolution 2x; try 2.5 or 3 if needed.
                    mat = fitz.Matrix(zoom_factor, zoom_factor)
                    for i in range(len(doc)):
                        page = doc.load_page(i)
                        pix = page.get_pixmap(matrix=mat)  # render page to an image
                        image_filename = f"{file.name}_page_{i+1}.png"
                        image_path = os.path.join(upload_dir, image_filename)
                        pix.save(image_path)  # Save image as PNG

                        # Run OCR (and any additional processing) on the image
                        detected_text = detect_text(image_path)
                        
                        structured_data.extend(detected_text)
                        image_urls.append({
                            "image_url": f"{settings.MEDIA_URL}uploads/{image_filename}",
                            "ocr_text": detected_text
                        })

                    extracted_data = structured_data
                    # Convert PDF pages to images using pdf2image
                    '''images = convert_from_path(file_path)
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
                    ''extracted_data = {
                        "pdf_text": text,
                        "structured_data": structured_data,
                        "pdf_images": image_urls
                    }''
                    extracted_data = structured_data'''

                # Save the extracted data to the database. If you updated your model to use a FileField called "file", use that.
                ExtractedData.objects.create(
                    file=file,  # Or use 'file=file' if you've updated your model
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
                    'image_url': f"{settings.MEDIA_URL}uploads/{file.name}",
                    #'file_url': f"{settings.MEDIA_URL}uploads/{file.name}",
                    'json_file_url': f"{settings.MEDIA_URL}uploads/{file.name}.json",
                    'individual_excel_url': f"{settings.MEDIA_URL}uploads/{excel_filename}",
                    'individual_csv_url': f"{settings.MEDIA_URL}uploads/{csv_filename}",
                    #'extracted_json': extracted_data
                    "extracted_data": extracted_data
                })
                """"image_url": image_url,
            "extracted_data": data.extracted_json,
            "uploaded_at": data.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
            "individual_excel_url": individual_excel_url,
            "individual_csv_url": individual_csv_url"""
            # Save combined DataFrame as Excel and CSV files
            combined_excel_filename = "combined.xlsx"
            combined_excel_path = os.path.join(upload_dir, combined_excel_filename)
            combined_df.to_excel(combined_excel_path, index=False)

            combined_csv_filename = "combined.csv"
            combined_csv_path = os.path.join(upload_dir, combined_csv_filename)
            combined_df.to_csv(combined_csv_path, index=False)

            context={
                'extracted_results': extracted_results,
                'combined_excel_file_url': f"{settings.MEDIA_URL}uploads/{combined_excel_filename}",
                'combined_csv_file_url': f"{settings.MEDIA_URL}uploads/{combined_csv_filename}"
            }
            return render(request, "show_extracted.html", context)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, "upload.html")

def index(request):
    uid = request.session.get('user_id')
    if not uid:
        return redirect('login')
    return render(request,"index.html")

def show_extracted_data(request):
    uid = request.session.get('user_id')
    if not uid:
        return redirect('login')
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
        image_url = settings.MEDIA_URL + data.file.url.split(settings.MEDIA_URL)[-1]
        
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

