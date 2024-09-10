import os
from django.shortcuts import render, redirect, get_object_or_404
from django import views
from .forms import *
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SystemSettings
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def LoginFormView(request):
    # If the user is already logged in, redirect to the dashboard
    if request.user.is_authenticated:
        return redirect("Dashboard")

    form = LoginForm(request.POST or None)

    if request.method == "POST":
        remember_me = request.POST.get('rememberMe') == 'on'
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)  # Authenticate with email

            if user is not None:
                if user.is_active:  # Check if the user is active
                    login(request, user)
                    if remember_me:
                        request.session.set_expiry(1209600)
                    messages.success(request, "Login Successful")
                    return redirect("Dashboard")
                else:
                    # Add error message if user account is deactivated
                    messages.error(request, "Your account is deactivated. Please contact the admin.")
            else:
                # Add error message for invalid credentials
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html", {"form": form})

class ForgotPasswordView(View):
    template_name = 'Admin/Auth/forgot_password.html'
    User = get_user_model()

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        user = self.User.objects.filter(email=email).first()

        if user:
            user.remember_token = get_random_string(40)
            user.token_created_at = timezone.now()
            user.save()
            reset_url = request.build_absolute_uri(reverse('reset_password', args=[user.remember_token]))

            context = {
                'user': user,
                'reset_url': reset_url
            }

            subject = 'Reset Your Password'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [user.email]
            html_content = render_to_string('Admin/Email/reset_password.html', context)

            msg = EmailMultiAlternatives(subject, '', from_email, to_email)
            msg.attach_alternative(html_content, "text/html")

            try:
                msg.send()
                messages.success(request, 'Please check your email for the reset link.')
            except Exception as e:
                messages.error(request, 'There was an error sending the email. Please try again later.')

            return redirect("login")
        else:
            messages.error(request, 'Email not found.')

        return redirect('forgot_password')

class ResetPasswordView(View):
    template_name = 'Admin/Auth/reset_password.html'
    User = get_user_model()

    def get(self, request, token):
        user = get_object_or_404(User, remember_token=token)

        # Check if the token has expired (1 hour expiration)
        expiration_time = timezone.now() - timedelta(hours=1)
        if user.token_created_at and user.token_created_at < expiration_time:
            messages.error(request, 'This reset link has expired.')
            return redirect('forgot_password')

        return render(request, self.template_name, {'token': token})

    def post(self, request, token):
        user = get_object_or_404(User, remember_token=token)

        # Check if the token has expired (1 hour expiration)
        expiration_time = timezone.now() - timedelta(hours=1)
        if user.token_created_at and user.token_created_at < expiration_time:
            messages.error(request, 'This reset link has expired.')
            return redirect('forgot_password')

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            user.set_password(password)
            if not user.email_verified_at:
                user.email_verified_at = timezone.now()
            user.remember_token = get_random_string(40)  # Invalidate the token
            user.token_created_at = None  # Clear the token creation time
            user.save()
            messages.success(request, 'Your password has been reset. You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')

        return render(request, self.template_name, {'token': token})

# Dashboard View
class Dashboard(LoginRequiredMixin, View):
    # Redirect the user to the login page if not authenticated
    login_url = "/"  # Specify your login URL if it's different
    redirect_field_name = (
        "redirect_to"  # Optional: specify where to redirect after login
    )

    # def get(self, request, *args, **kwargs):
    #     return render(request, 'Admin/Dashboard.html')

    def get(self, request, *args, **kwargs):
        context = {"breadcrumb": {"parent": "Admin", "child": "Dashboard"}}
        return render(request, "Admin/Dashboard.html", context)


def logout_view(request):
    logout(request)
    return redirect("login")


class Table(LoginRequiredMixin, views.View):
    def get(self, request, *args, **kwargs):
        return render(request, "table/datatable-basic-init.html")


# User Profile View
class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        context = {
            "user": user,
            "breadcrumb": {"parent": "Acccount", "child": "Profile"},
        }

        return render(request, "Admin/User/user_profile.html", context)

    def post(self, request):
        user = request.user

        return render(request, "Admin/User/user_profile.html", {"user": user})


@method_decorator(login_required, name="dispatch")
class UserUpdateProfileView(View):
    def get(self, request, *args, **kwargs):
        form = UserUpdateProfileForm(instance=request.user)
        password_change_form = CustomPasswordChangeForm(user=request.user)
        return render(
            request,
            "Admin/User/edit_profile.html",
            {
                "form": form,
                "password_change_form": password_change_form,
                "breadcrumb": {"parent": "Acccount", "child": "Edit Profile"},
            },
        )

    def post(self, request, *args, **kwargs):
        if "change_password" in request.POST:
            # Handle password change
            password_change_form = CustomPasswordChangeForm(
                user=request.user, data=request.POST
            )
            if password_change_form.is_valid():
                user = password_change_form.save()
                logout(request)  # Log out the user after password change
                messages.success(
                    request,
                    "Your password has been changed successfully. Please log in again.",
                )
                return redirect("login")
            else:
                for field in password_change_form:
                    for error in field.errors:
                        messages.error(request, error)
                form = UserUpdateProfileForm(instance=request.user)
                return render(
                    request,
                    "Admin/User/edit_profile.html",
                    {"form": form, "password_change_form": password_change_form},
                )
        else:
            # Handle profile update
            user = request.user
            old_profile_picture = user.profile_picture
            old_card_header = user.card_header

            form = UserUpdateProfileForm(
                request.POST, instance=user, files=request.FILES
            )
            if form.is_valid():
                # Handle profile picture update
                if "profile_picture" in request.FILES:
                    if old_profile_picture and os.path.isfile(
                        os.path.join(settings.MEDIA_ROOT, str(old_profile_picture))
                    ):
                        os.remove(
                            os.path.join(settings.MEDIA_ROOT, str(old_profile_picture))
                        )
                elif "profile_picture-clear" in request.POST:
                    user.profile_picture = None

                # Handle card header update
                if "card_header" in request.FILES:
                    if old_card_header and os.path.isfile(
                        os.path.join(settings.MEDIA_ROOT, str(old_card_header))
                    ):
                        os.remove(
                            os.path.join(settings.MEDIA_ROOT, str(old_card_header))
                        )
                elif "card_header-clear" in request.POST:
                    user.card_header = None

                user = form.save()
                messages.success(request, "Your profile has been updated successfully.")
                return redirect("edit_profile")
            else:
                for field in form:
                    for error in field.errors:
                        messages.error(request, error)
                password_change_form = CustomPasswordChangeForm(user=request.user)
                return render(
                    request,
                    "Admin/User/edit_profile.html",
                    {"form": form, "password_change_form": password_change_form},
                )


# SytemSettings view
class System_Settings(LoginRequiredMixin, View):
    login_url = "/"
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):
        system_settings = SystemSettings.objects.first()  # Fetch the first record
        return render(
            request,
            "Admin/System_Settings.html",
            {
                "system_settings": system_settings,
                "MEDIA_URL": settings.MEDIA_URL,
                "breadcrumb": {
                    "parent": "Admin",
                    "child": "System Settings",
                },  # Pass MEDIA_URL to the template
            },
        )

    def post(self, request, *args, **kwargs):
        system_settings = SystemSettings.objects.first()
        if not system_settings:
            system_settings = SystemSettings()

        fs = FileSystemStorage(
            location=os.path.join(settings.MEDIA_ROOT, "System_Settings")
        )

        errors = {}
        success = False

        try:
            # Handle fav_icon
            if "fav_icon" in request.FILES:
                if system_settings.fav_icon:
                    old_fav_icon_path = os.path.join(
                        settings.MEDIA_ROOT, system_settings.fav_icon
                    )
                    if os.path.isfile(old_fav_icon_path):
                        os.remove(old_fav_icon_path)
                fav_icon_file = request.FILES["fav_icon"]
                fav_icon_filename = "favicon.jpg"
                fs.save(fav_icon_filename, fav_icon_file)
                system_settings.fav_icon = os.path.join(
                    "System_Settings", fav_icon_filename
                )

            # Handle footer_logo
            if "footer_logo" in request.FILES:
                if system_settings.footer_logo:
                    old_footer_logo_path = os.path.join(
                        settings.MEDIA_ROOT, system_settings.footer_logo
                    )
                    if os.path.isfile(old_footer_logo_path):
                        os.remove(old_footer_logo_path)
                footer_logo_file = request.FILES["footer_logo"]
                footer_logo_filename = "footer_logo.jpg"
                fs.save(footer_logo_filename, footer_logo_file)
                system_settings.footer_logo = os.path.join(
                    "System_Settings", footer_logo_filename
                )

            # Handle header_logo
            if "header_logo" in request.FILES:
                if system_settings.header_logo:
                    old_header_logo_path = os.path.join(
                        settings.MEDIA_ROOT, system_settings.header_logo
                    )
                    if os.path.isfile(old_header_logo_path):
                        os.remove(old_header_logo_path)
                header_logo_file = request.FILES["header_logo"]
                header_logo_filename = "header_logo.jpg"
                fs.save(header_logo_filename, header_logo_file)
                system_settings.header_logo = os.path.join(
                    "System_Settings", header_logo_filename
                )

            # Validate and save other fields
            system_settings.website_name_english = request.POST.get(
                "website_name_english"
            )
            system_settings.website_name_arabic = request.POST.get(
                "website_name_arabic"
            )
            system_settings.phone = request.POST.get("phone")
            system_settings.email = request.POST.get("email")
            system_settings.address = request.POST.get("address")
            system_settings.instagram = request.POST.get("instagram")
            system_settings.facebook = request.POST.get("facebook")
            system_settings.snapchat = request.POST.get("snapchat")
            system_settings.linkedin = request.POST.get("linkedin")
            system_settings.youtube = request.POST.get("youtube")

            fields = {
                    'website_name_english': "This field is required.",
                    'website_name_arabic': "This field is required.",
                    'phone': "This field is required.",
                    'email': "This field is required.",
                    'address': "This field is required."
                }

            for field, error_message in fields.items():
                if not getattr(system_settings, field):
                    errors[field] = error_message

            # Add additional validations as needed

            if errors:
                messages.error(request, "Please correct the errors below.")
            else:
                system_settings.save()
                success = True
                messages.success(request, "System settings were successfully updated.")
        
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        if errors:
            return render(request, "Admin/System_Settings.html", {
                "system_settings": system_settings,
                "MEDIA_URL": settings.MEDIA_URL,
                "breadcrumb": {
                    "parent": "Admin",
                    "child": "System Settings",
                },
                "errors": errors,
            })
        elif success:
            return redirect("Dashboard")
        else:
            return redirect("Dashboard")


# User Active & Deactive Function
class ToggleUserStatusView(View):
    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        new_status = request.POST.get("status")

        # Check if the user is a superuser
        if user.role_id == 1:
            messages.error(request, "Superuser status cannot be changed.")
            return redirect("user_list")

        # Check if the current user is trying to deactivate their own account
        if user == request.user and new_status == "deactivate":
            messages.info(
                request, "Your account has been deactivated. Please log in again."
            )
            user.is_active = False
            user.save()
            return redirect(reverse("login"))

        # Update the user's status
        if new_status == "activate":
            user.is_active = True
            messages.success(request, f"{user.username} has been activated.")
        elif new_status == "deactivate":
            user.is_active = False
            messages.success(request, f"{user.username} has been deactivated.")

        user.save()

        return redirect("user_list")


# User Crud
class UserListView(LoginRequiredMixin, View):
    template_name = "Admin/User_List.html"

    def get(self, request):
        User = get_user_model()  # Get the custom user model
        users = User.objects.all()
        roles = Role.objects.all()
        return render(
            request,
            self.template_name,
            {
                "users": users,
                "roles": roles,
                "breadcrumb": {"parent": "User", "child": "User List"},
            },
        )

class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'phone', 'role']

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email


class UserEditView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = get_object_or_404(get_user_model(), id=user_id)
        roles = Role.objects.all()
        return JsonResponse(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role.id if user.role else None,
            }
        )

    @method_decorator(csrf_exempt)
    def post(self, request, user_id):
        user = get_object_or_404(get_user_model(), id=user_id)
        form = UserEditForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            # Use Django messages to pass success message
            messages.success(request, f"User {user.username} was successfully updated.")
            return JsonResponse({"success": True})
        else:
            # Return form errors if the form is invalid
            return JsonResponse({"success": False, "errors": form.errors})

class UserDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        messages.success(request, f"User {user.username} was successfully deleted.")
        return redirect("user_list")  # Redirect to the user list after successful deletion

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        print(user)
        print(user.role_id)
        if user.role_id == 1 or user.role is None:
            messages.error(request,"SuperUser Can not deleted.")
            print(messages.success(request,"SuperUser Can not deleted."))
            return redirect("user_list")
        else:
            user.delete()
            messages.success(request, f"User {user.username} was successfully deleted.")
            return redirect("user_list")  # Redirect to the user list after successful deletion


# Category CRUD Views
class CategoryCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = CategoryForm()
        return render(request, "forms/category_form.html", {"form": form})

    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            # Check for existing category with the same name
            name = form.cleaned_data.get("name")
            if Category.objects.filter(name=name).exists():
                messages.error(request, "A category with this name already exists.")
                return redirect(
                    "category_list"
                )  # Redirect back to category_list with an error message
            form.save()
            messages.success(request, "Category was successfully created.")
            return redirect("category_list")
        else:
            messages.error(
                request,
                "There was an error creating the category. Please ensure all fields are filled out correctly.",
            )
        return redirect("category_list")


class CategoryUpdateView(LoginRequiredMixin, View):
    template_name = "forms/category_form.html"

    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        form = CategoryForm(instance=category)
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category was successfully updated.")
            return redirect("category_list")
        else:
            messages.error(
                request,
                "There was an error updating the category. Please ensure all fields are filled out correctly.",
            )
        return render(request, self.template_name, {"form": form})


class CategoryDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        messages.success(request, "Category was successfully deleted.")
        return redirect("category_list")

    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        messages.success(request, "Category was successfully deleted.")
        return redirect("category_list")


class CategoryListView(LoginRequiredMixin, View):
    template_name = "Admin/Category_List.html"

    def get(self, request):
        categories = Category.objects.all()
        return render(
            request,
            self.template_name,
            {
                "categories": categories,
                "breadcrumb": {"parent": "User", "child": "Category"},
            },
        )


# Role CRUD Views
class RoleCreateView(LoginRequiredMixin, View):
    template_name = "Admin/User_Role.html"

    def get(self, request):
        form = RoleForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Role created successfully.")
            return redirect("role_list")
        messages.error(
            request,
            "There was an error creating the role. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class RoleUpdateView(LoginRequiredMixin, View):
    template_name = "Admin/User_Role.html"  # Fixed template name

    def get(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        form = RoleForm(instance=role)
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, "Role was successfully updated.")
            return redirect("role_list")
        messages.error(
            request,
            "There was an error updating the role. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class RoleDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        role.delete()
        messages.success(request, "Role was successfully deleted.")
        return redirect("role_list")

    def post(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        role.delete()
        messages.success(request, "Role was successfully deleted.")
        return redirect("role_list")


class RoleListView(LoginRequiredMixin, View):
    template_name = "Admin/User_Role.html"

    def get(self, request):
        roles = Role.objects.all()
        return render(
            request,
            self.template_name,
            {"roles": roles, "breadcrumb": {"parent": "User", "child": "Role"}},
        )


# Gender CRUD Views
class GenderCreateView(LoginRequiredMixin, View):
    template_name = "forms/gender_form.html"

    def get(self, request):
        form = GenderForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = GenderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Gender created successfully.")
            return redirect("gender_list")
        messages.error(
            request,
            "There was an error creating the gender. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class GenderUpdateView(LoginRequiredMixin, View):
    template_name = "forms/gender_form.html"

    def get(self, request, pk):
        gender = get_object_or_404(UserGender, pk=pk)
        form = GenderForm(instance=gender)
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk):
        gender = get_object_or_404(UserGender, pk=pk)
        form = GenderForm(request.POST, instance=gender)
        if form.is_valid():
            form.save()
            messages.success(request, "Gender was successfully updated.")
            return redirect("gender_list")
        messages.error(
            request,
            "There was an error updating the gender. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class GenderDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        gender = get_object_or_404(UserGender, pk=pk)
        gender.delete()
        messages.success(request, "Gender was successfully deleted.")
        return redirect("gender_list")

    def post(self, request, pk):
        gender = get_object_or_404(UserGender, pk=pk)
        gender.delete()
        messages.success(request, "Gender was successfully deleted.")
        return redirect("gender_list")


class GenderListView(LoginRequiredMixin, View):
    template_name = "Admin/General_Settings/Gender.html"

    def get(self, request):
        genders = UserGender.objects.all()
        return render(
            request,
            self.template_name,
            {
                "genders": genders,
                "breadcrumb": {"parent": "General Settings", "child": "Gender"},
            },
        )


# GameType CRUD Views
class GameTypeCreateView(LoginRequiredMixin, View):
    template_name = "forms/gametype_form.html"

    def get(self, request):
        form = GameTypeForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = GameTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Game type created successfully.")
            return redirect("gametype_list")
        messages.error(
            request,
            "There was an error creating the game type. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class GameTypeUpdateView(LoginRequiredMixin, View):
    template_name = "forms/gametype_form.html"

    def get(self, request, pk):
        gametype = get_object_or_404(GameType, pk=pk)
        form = GameTypeForm(instance=gametype)
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk):
        gametype = get_object_or_404(GameType, pk=pk)
        form = GameTypeForm(request.POST, instance=gametype)
        if form.is_valid():
            form.save()
            messages.success(request, "Game type was successfully updated.")
            return redirect("gametype_list")
        messages.error(
            request,
            "There was an error updating the game type. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class GameTypeDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        gametype = get_object_or_404(GameType, pk=pk)
        gametype.delete()
        messages.success(request, "Game type was successfully deleted.")
        return redirect("gametype_list")

    def post(self, request, pk):
        gametype = get_object_or_404(GameType, pk=pk)
        gametype.delete()
        messages.success(request, "Game type was successfully deleted.")
        return redirect("gametype_list")


class GameTypeListView(LoginRequiredMixin, View):
    template_name = "Admin/General_Settings/GameType.html"

    def get(self, request):
        gametypes = GameType.objects.all()
        return render(
            request,
            self.template_name,
            {
                "gametypes": gametypes,
                "breadcrumb": {"parent": "General Settings", "child": "Game Type"},
            },
        )


# fieldcapacity CRUD Views
class FieldCapacityCreateView(LoginRequiredMixin, View):
    template_name = "forms/fieldcapacity_form.html"

    def get(self, request):
        form = FieldCapacityForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = FieldCapacityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Field Capacity created successfully.")
            return redirect("fieldcapacity_list")
        messages.error(
            request,
            "There was an error creating the Field Capacity. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class FieldCapacityUpdateView(LoginRequiredMixin, View):
    template_name = "forms/fieldcapacity_form.html"

    def get(self, request, pk):
        fieldcapacity = get_object_or_404(FieldCapacity, pk=pk)
        form = FieldCapacityForm(instance=fieldcapacity)
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk):
        fieldcapacity = get_object_or_404(FieldCapacity, pk=pk)
        form = FieldCapacityForm(request.POST, instance=fieldcapacity)
        if form.is_valid():
            form.save()
            messages.success(request, "Field Capacity updated successfully.")
            return redirect("fieldcapacity_list")
        messages.error(
            request,
            "There was an error updating the game type. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class FieldCapacityDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        fieldcapacity = get_object_or_404(FieldCapacity, pk=pk)
        fieldcapacity.delete()
        messages.success(request, "Field Capacity successfully deleted.")
        return redirect("fieldcapacity_list")

    def post(self, request, pk):
        fieldcapacity = get_object_or_404(FieldCapacity, pk=pk)
        fieldcapacity.delete()
        messages.success(request, "Field Capacity successfully deleted.")
        return redirect("fieldcapacity_list")


class FieldCapacityListView(LoginRequiredMixin, View):
    template_name = "Admin/General_Settings/FieldCapacity.html"

    def get(self, request):
        fieldcapacitys = FieldCapacity.objects.all()
        return render(
            request,
            self.template_name,
            {
                "fieldcapacitys": fieldcapacitys,
                "breadcrumb": {"parent": "General Settings", "child": "Field Capacity"},
            },
        )


# GroundMaterials CRUD Views
class GroundMaterialCreateView(LoginRequiredMixin, View):
    template_name = "forms/groundmaterial_form.html"

    def get(self, request):
        form = GroundMaterialForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = GroundMaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Field Capacity created successfully.")
            return redirect("groundmaterial_list")
        messages.error(
            request,
            "There was an error creating the Field Capacity. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class GroundMaterialUpdateView(LoginRequiredMixin, View):
    template_name = "forms/groundmaterial_form.html"

    def get(self, request, pk):
        groundmaterial = get_object_or_404(GroundMaterial, pk=pk)
        form = GroundMaterialForm(instance=groundmaterial)
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk):
        groundmaterial = get_object_or_404(GroundMaterial, pk=pk)
        form = GroundMaterialForm(request.POST, instance=groundmaterial)
        if form.is_valid():
            form.save()
            messages.success(request, "Field Capacity updated successfully.")
            return redirect("groundmaterial_list")
        messages.error(
            request,
            "There was an error updating the game type. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class GroundMaterialDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        groundmaterial = get_object_or_404(GroundMaterial, pk=pk)
        groundmaterial.delete()
        messages.success(request, "Field Capacity successfully deleted.")
        return redirect("groundmaterial_list")

    def post(self, request, pk):
        groundmaterial = get_object_or_404(GroundMaterial, pk=pk)
        groundmaterial.delete()
        messages.success(request, "Field Capacity successfully deleted.")
        return redirect("groundmaterial_list")


class GroundMaterialListView(LoginRequiredMixin, View):
    template_name = "Admin/General_Settings/GroundMaterial.html"

    def get(self, request):
        groundmaterials = GroundMaterial.objects.all()
        return render(
            request,
            self.template_name,
            {
                "groundmaterials": groundmaterials,
                "breadcrumb": {
                    "parent": "General Settings",
                    "child": "Ground Material",
                },
            },
        )


# Tournament Style CRUD Views
class TournamentStyleCreateView(LoginRequiredMixin, View):
    template_name = "forms/tournamentstyle_form.html"

    def get(self, request):
        form = TournamentStyleForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = TournamentStyleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Field Capacity created successfully.")
            return redirect("tournamentstyle_list")
        messages.error(
            request,
            "There was an error creating the Field Capacity. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class TournamentStyleUpdateView(LoginRequiredMixin, View):
    template_name = "forms/tournamentstyle_form.html"

    def get(self, request, pk):
        tournamentstyle = get_object_or_404(TournamentStyle, pk=pk)
        form = TournamentStyleForm(instance=tournamentstyle)
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk):
        tournamentstyle = get_object_or_404(TournamentStyle, pk=pk)
        form = TournamentStyleForm(request.POST, instance=tournamentstyle)
        if form.is_valid():
            form.save()
            messages.success(request, "Field Capacity updated successfully.")
            return redirect("tournamentstyle_list")
        messages.error(
            request,
            "There was an error updating the game type. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class TournamentStyleDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        tournamentstyle = get_object_or_404(TournamentStyle, pk=pk)
        tournamentstyle.delete()
        messages.success(request, "Field Capacity successfully deleted.")
        return redirect("tournamentstyle_list")

    def post(self, request, pk):
        tournamentstyle = get_object_or_404(TournamentStyle, pk=pk)
        tournamentstyle.delete()
        messages.success(request, "Field Capacity successfully deleted.")
        return redirect("tournamentstyle_list")


class TournamentStyleListView(LoginRequiredMixin, View):
    template_name = "Admin/General_Settings/TournamentStyle.html"

    def get(self, request):
        tournamentstyles = TournamentStyle.objects.all()
        return render(
            request,
            self.template_name,
            {
                "tournamentstyles": tournamentstyles,
                "breadcrumb": {"parent": "General Settings", "child": "Tournaments"},
            },
        )


# Event Type CRUD Views
class EventTypeCreateView(LoginRequiredMixin, View):
    template_name = "forms/eventtype_form.html"

    def get(self, request):
        form = EventTypeForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = EventTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Field Capacity created successfully.")
            return redirect("eventtype_list")
        messages.error(
            request,
            "There was an error creating the Field Capacity. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class EventTypeUpdateView(LoginRequiredMixin, View):
    template_name = "forms/eventtype_form.html"

    def get(self, request, pk):
        eventtype = get_object_or_404(EventType, pk=pk)
        form = EventTypeForm(instance=eventtype)
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk):
        eventtype = get_object_or_404(EventType, pk=pk)
        form = EventTypeForm(request.POST, instance=eventtype)
        if form.is_valid():
            form.save()
            messages.success(request, "Field Capacity updated successfully.")
            return redirect("eventtype_list")
        messages.error(
            request,
            "There was an error updating the game type. Please ensure all fields are filled out correctly.",
        )
        return render(request, self.template_name, {"form": form})


class EventTypeDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        eventtype = get_object_or_404(EventType, pk=pk)
        eventtype.delete()
        messages.success(request, "Field Capacity successfully deleted.")
        return redirect("eventtype_list")

    def post(self, request, pk):
        eventtype = get_object_or_404(EventType, pk=pk)
        eventtype.delete()
        messages.success(request, "Field Capacity successfully deleted.")
        return redirect("eventtype_list")


class EventTypeListView(LoginRequiredMixin, View):
    template_name = "Admin/General_Settings/EventType.html"

    def get(self, request):
        eventtypes = EventType.objects.all()
        return render(
            request,
            self.template_name,
            {
                "eventtypes": eventtypes,
                "breadcrumb": {"parent": "General Settings", "child": "Event Types"},
            },
        )
