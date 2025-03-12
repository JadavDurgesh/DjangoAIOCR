# Generated by Django 5.1.6 on 2025-03-03 08:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_company'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=255)),
                ('user_designation', models.CharField(max_length=255)),
                ('project_name', models.CharField(max_length=255)),
                ('team', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancel', 'Cancel'), ('Droped', 'Droped')], default='Active', max_length=10)),
                ('budget', models.DecimalField(decimal_places=2, max_digits=10)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_details', to='myapp.company')),
            ],
        ),
    ]
