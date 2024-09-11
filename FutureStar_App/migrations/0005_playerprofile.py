# Generated by Django 4.2.11 on 2024-09-11 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FutureStar_App', '0004_delete_gametype'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(blank=True, max_length=255, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('age', models.PositiveIntegerField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, max_length=10, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('nationality', models.CharField(blank=True, max_length=100, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('height', models.PositiveIntegerField(blank=True, null=True)),
                ('main_playing_position', models.CharField(blank=True, max_length=50, null=True)),
                ('secondary_playing_position', models.CharField(blank=True, max_length=50, null=True)),
                ('playing_foot', models.CharField(blank=True, max_length=10, null=True)),
                ('favourite_local_team', models.CharField(blank=True, max_length=100, null=True)),
                ('favourite_team', models.CharField(blank=True, max_length=100, null=True)),
                ('favourite_local_player', models.CharField(blank=True, max_length=100, null=True)),
                ('favourite_player', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
