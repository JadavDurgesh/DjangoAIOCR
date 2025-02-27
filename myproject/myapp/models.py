from django.db import models

# Create your models here.


class ExtractedData(models.Model):
    image = models.ImageField(upload_to="uploads/")
    extracted_json = models.JSONField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Extracted Data from {self.image.name}"
