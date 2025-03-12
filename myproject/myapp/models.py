from django.db import models

# Create your models here.
from django.core.validators import RegexValidator

class Company(models.Model):
    company_name = models.CharField(max_length=255)
    company_email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # In production, hash passwords!
    # You can use a RegexValidator to ensure a valid 10-digit phone number:
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\d{10}$', message="Enter a valid 10-digit phone number")]
    )
    address = models.TextField()
    company_pan = models.CharField(max_length=10)
    company_gst = models.CharField(max_length=15)

    def __str__(self):
        return self.company_name
    
class CompanyDetails(models.Model):
    user = models.CharField(max_length=255)
    user_designation = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255)
    team = models.CharField(max_length=255)
    status = models.CharField(choices=(("Active", "Active"), ("Inactive", "Inactive"), ("Pending", "Pending"), ("Completed","Completed"),("Cancel","Cancel"),("Droped","Droped")), default="Active", max_length=10)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    company = models.ForeignKey(Company, on_delete=models.CASCADE , related_name="company_details")
    def __str__(self):
        return self.project_name

class ExtractedData(models.Model):
    file = models.FileField(upload_to="uploads/", null=True)
    extracted_json = models.JSONField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Extracted Data from {self.image.name}"


class Users(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10)
    password = models.CharField(max_length=50)
    otp = models.IntegerField(default=0000)

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.email} {self.phone_number}"