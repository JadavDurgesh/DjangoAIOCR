from django.urls import path
from .views import *

urlpatterns = [
    path('index/', index, name="index"),
    path('upload/', UploadExtractFileView, name='upload'),
    path('company_create/', company_create, name='company_create'),
    path('show-extracted/', show_extracted_data, name='show_extracted'),
    path('companies/', company_list, name='company_list'),
    path('companies/<int:company_id>/', company_details, name='company_details'),
    path('', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('my_account/', my_account, name='my_account'),
    path('change_password/', change_password, name='change_password'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('delete_account/', delete_account, name='delete_account'),
]
