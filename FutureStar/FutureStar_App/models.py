from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from django.contrib.auth.hashers import make_password, check_password

# Role Model
class Role(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# User Category Model
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, email, password, **extra_fields)


# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=150, unique=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    card_header = models.ImageField(upload_to="card_header/", null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=255)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    remember_token = models.CharField(max_length=255,null=True, blank=True)
    token_created_at = models.DateTimeField(null=True, blank=True)  # Add this field
    email_verified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username


# System Settings Model
class SystemSettings(models.Model):
    fav_icon = models.CharField(max_length=255, null=True, blank=True)
    footer_logo = models.CharField(max_length=255, null=True, blank=True)
    header_logo = models.CharField(max_length=255, null=True, blank=True)
    website_name_english = models.CharField(max_length=255)
    website_name_arabic = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    instagram = models.TextField(null=True, blank=True)
    facebook = models.TextField(null=True, blank=True)
    snapchat = models.TextField(null=True, blank=True)
    linkedin = models.TextField(null=True, blank=True)
    youtube = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.website_name_english


# gender Model
class UserGender(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# # Game Type  Model
# class GameType(models.Model):
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name


# Field Capacity  Model
class FieldCapacity(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Ground Materials Model
class GroundMaterial(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Tournamebt Style Model
class TournamentStyle(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Event Types Model
class EventType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


#User Profile
class Player_Profile(models.Model):
    
    user_id = models.ForeignKey(User, on_delete=models.CASCADE ,blank=True, null=True)
    
    fullname = models.CharField(max_length=255, blank=True, null=True)
    
    username = models.CharField(max_length=150, unique=True,default='')
        
    password = models.CharField(max_length=128,default='')  
    
    date_joined = models.DateTimeField(auto_now_add=True)
    
    is_active = models.BooleanField(default=True)
    
    username = models.CharField(max_length=255,null = False)
    
    Phone_Number = models.PositiveIntegerField(null=False,default='')
    
    bio = models.TextField(blank=True, null=True)

    date_of_birth = models.DateField(blank=True, null=True)

    age = models.PositiveIntegerField(blank=True, null=True)

    gender = models.CharField(max_length=10, blank=True, null=True)

    country = models.CharField(max_length=100, blank=True, null=True)

    city = models.CharField(max_length=100, blank=True, null=True)

    nationality = models.CharField(max_length=100, blank=True, null=True)

    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    height = models.PositiveIntegerField(blank=True, null=True)

    main_playing_position = models.CharField(max_length=50, blank=True, null=True)

    secondary_playing_position = models.CharField(max_length=50, blank=True, null=True)

    playing_foot = models.CharField(max_length=10, blank=True, null=True)

    favourite_local_team = models.CharField(max_length=100, blank=True, null=True)

    favourite_team = models.CharField(max_length=100, blank=True, null=True)

    favourite_local_player = models.CharField(max_length=100, blank=True, null=True)

    favourite_player = models.CharField(max_length=100, blank=True, null=True)
    #data
    def set_password(self, raw_password):
         self.password = make_password(raw_password)
         self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return self.fullname if self.fullname else 'Player Profile'
        
class News(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    news_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title    

# class UserPost(models.Model):
    
#     user_id = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)  
#     description = models.TextField() 
#     photo = models.CharField(upload_to='profile_pics/',null=True, blank=True)  
        
#     class Meta:
#         db_table = "FutureStar_App_UserPost"

# class Sponsor(models.Model):
#     sponsor_name = models.CharField(max_length=255)  
#     sponsor_logo = models.ImageField(upload_to='sponsor_logos/')  
#     phone_number = models.CharField(max_length=20, blank=True, null=True)  
#     email_address = models.EmailField(blank=True, null=True)  

#     def __str__(self):
#         return self.sponsor_name

# class EditStuff(models.Model):
    
#     role = models.CharField(max_length=20)  
#     name = models.CharField(max_length=255)  
#     profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  
#     phone_number = models.CharField(max_length=20, blank=True, null=True) 
#     email_address = models.EmailField(blank=True, null=True)  
#     country = models.CharField(max_length=100)  
#     city = models.CharField(max_length=100)  

#     def __str__(self):
#         return self.name

# class PlayerBranch(models.Model):
#     name = models.CharField(max_length=255)
    
#     position = models.CharField(max_length=100)
    
#     profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

#     phone_number = models.CharField(max_length=20, blank=True, null=True)
    
#     email_address = models.EmailField(blank=True, null=True)
    
#     country = models.CharField(max_length=100)
    
#     city = models.CharField(max_length=100)
    
#     weight = models.FloatField()
    
#     height = models.FloatField()
    
#     age = models.PositiveIntegerField()
    
#     date_of_birth = models.DateField()
    
#     def __str__(self):
#         return self.name    

# class FriendlyGame(models.Model):
    # game_number = models.PositiveIntegerField(unique=True)
    # start_date = models.DateField()
    # start_time = models.TimeField()
    # team_A = models.CharField(max_length=255)
    # team_B = models.CharField(max_length=255)
    # game_field = models.CharField(max_length=255)
    # referee_name = models.CharField(max_length=255)
    # def __str__(self):
    #     return f"Game {self.game_number}: {self.team_A} vs {self.team_B} on {self.start_date}"
    # 

# News Module  Model

 