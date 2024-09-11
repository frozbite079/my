# Generated by Django 4.2.11 on 2024-09-11 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FutureStar_App', '0009_editstuff'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerBranch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('position', models.CharField(max_length=100)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profile_images/')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('email_address', models.EmailField(blank=True, max_length=254, null=True)),
                ('country', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('weight', models.FloatField()),
                ('height', models.FloatField()),
                ('age', models.PositiveIntegerField()),
                ('date_of_birth', models.DateField()),
            ],
        ),
    ]
