
from django.contrib import admin
from django.utils.html import format_html
import json
from .models import ExtractedData

class ExtractedDataAdmin(admin.ModelAdmin):
    list_display = ("image_preview", "formatted_json", "uploaded_at")  # Show preview & formatted JSON
    readonly_fields = ("image_preview", "formatted_json")  # Make fields read-only

    def image_preview(self, obj):
        """Displays a small preview of the uploaded image."""
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius:5px;" />', obj.image.url)
        return "No Image"

    def formatted_json(self, obj):
        """Formats JSON data with syntax highlighting."""
        if obj.extracted_json:
            pretty_json = json.dumps(obj.extracted_json, indent=4, ensure_ascii=False)
            return format_html('<pre style="background: #282c34; color: #abb2bf; padding:10px; border-radius:5px;">{}</pre>', pretty_json)
        return "No JSON Data"

    image_preview.short_description = "Image Preview"
    formatted_json.short_description = "Extracted JSON"

admin.site.register(ExtractedData, ExtractedDataAdmin)