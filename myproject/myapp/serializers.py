from rest_framework import serializers
from .models import ExtractedData

class ExtractedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedData
        fields = ['id', 'image', 'extracted_json', 'uploaded_at']
