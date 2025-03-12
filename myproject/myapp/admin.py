
from django.contrib import admin
from django.utils.html import format_html
import json
from .models import *

class ExtractedDataAdmin(admin.ModelAdmin):
    list_display = ("image_preview", "formatted_json", "uploaded_at")  # Show preview & formatted JSON
    readonly_fields = ("image_preview", "formatted_json")  # Make fields read-only

    def image_preview(self, obj):
        """Displays a small preview of the uploaded image."""
        if obj.file:
            return format_html('<img src="{}" width="100" height="100" style="border-radius:5px;" />', obj.file.url)
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

class CompanyDetailsInline(admin.TabularInline):
    model = CompanyDetails
    extra = 1

class CompanyDetailsAdmin(admin.ModelAdmin):
    list_display = ("company","user", "user_designation", "project_name", "team", "status", "budget")
    search_fields = ("company","user", "user_designation", "project_name", "team", "status", "budget")
    list_filter = ("status",)
admin.site.register(CompanyDetails, CompanyDetailsAdmin)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("company_name", "company_email", "phone", "address", "company_pan", "company_gst")
    search_fields = ("company_name", "company_email", "phone", "company_pan", "company_gst")
    fieldsets = (
        ("Basic Information", {
            "fields": ("company_name", "company_email", "phone", "company_pan", "company_gst","password"),
            "description":"This is the basic information of the company." ,
        }),
        ("Address", {
            "fields": ("address",),
            "description":"This is the address of the company."
        }),
    )
    inlines = [CompanyDetailsInline]

@admin.register(Users)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'phone_number','otp')#, 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    #list_filter = ('is_staff', 'is_active')
    def username(self, obj):
        return obj.first_name + " " + obj.last_name
    username.short_description = "Full Name"
    

    