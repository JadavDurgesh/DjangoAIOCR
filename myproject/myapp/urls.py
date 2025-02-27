from django.urls import path
from .views import index,UploadExtractImageView, GetExtractedDataView

urlpatterns = [
    path('', index, name="index"),
    path('upload-image/', UploadExtractImageView.as_view(), name='upload-image'),
    path('get-extracted-data/', GetExtractedDataView.as_view(), name='get-extracted-data'),
]
