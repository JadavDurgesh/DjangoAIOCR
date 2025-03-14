# Generated by Django 5.1.6 on 2025-03-03 07:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_remove_extracteddata_image_extracteddata_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=255)),
                ('company_email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('phone', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Enter a valid 10-digit phone number', regex='^\\d{10}$')])),
                ('address', models.TextField()),
                ('company_pan', models.CharField(max_length=10)),
                ('company_gst', models.CharField(max_length=15)),
            ],
        ),
    ]
