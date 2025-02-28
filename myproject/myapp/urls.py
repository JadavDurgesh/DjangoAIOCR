from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="index"),
    path('upload/', UploadExtractDataView.as_view(), name='upload'),
    path('get-extracted-data/', GetExtractedDataView.as_view(), name='get-extracted-data'),
]
