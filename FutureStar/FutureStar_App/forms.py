from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import password_validation


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={"placeholder": "Email", "class": "form-control"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password check", "class": "form-control"}
        )
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


# User Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter category name"}),
        }


# Role Form
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter role name"}),
        }


# Gender Form
class GenderForm(forms.ModelForm):
    class Meta:
        model = UserGender
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter UserGender"}),
        }


# # GameType Form
# class GameTypeForm(forms.ModelForm):
#     class Meta:
#         model = GameType
#         fields = ["name"]
#         widgets = {
#             "name": forms.TextInput(attrs={"placeholder": "Enter GameType"}),
#         }


# Field Capacity Form
class FieldCapacityForm(forms.ModelForm):
    class Meta:
        model = FieldCapacity
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter Field Capacity"}),
        }


# Ground Material Form
class GroundMaterialForm(forms.ModelForm):
    class Meta:
        model = GroundMaterial
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter Ground Material"}),
        }


# Tournament Style Form
class TournamentStyleForm(forms.ModelForm):
    class Meta:
        model = TournamentStyle
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter Tournament Style"}),
        }


# Event Type Style Form
class EventTypeForm(forms.ModelForm):
    class Meta:
        model = EventType
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter Event Type"}),
        }


class UserUpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "role",
            "profile_picture",
            "card_header",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set common attributes for all fields
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
            field.required = False

        # Make specific fields read-only
        readonly_fields = ["username", "email", "phone", "role"]
        for field_name in readonly_fields:
            self.fields[field_name].widget.attrs["readonly"] = True


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=("Old password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "autofocus": True,
                "class": "form-control",
            }
        ),
    )
    new_password1 = forms.CharField(
        label=("New password"),
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "class": "form-control"}
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),  # type: ignore
    )
    new_password2 = forms.CharField(
        label=("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "class": "form-control"}
        ),
    )
