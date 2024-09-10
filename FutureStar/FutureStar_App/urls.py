from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.shortcuts import redirect


def custom_404_view(request, exception=None):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if the user is not authenticated
    return render(request, 'error\error.html', status=404)

handler404 = 'FutureStar_App.urls.custom_404_view'

urlpatterns = [


    #Login URL
    path('', LoginFormView,name="login"),


    #Dashboard URL
    path('Dashboard/', Dashboard.as_view(),name="Dashboard"),


    #Logout URL
    path('logout/', logout_view, name='logout'),  # Add the logout path here

    # Forgot Password 
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<str:token>/', ResetPasswordView.as_view(), name='reset_password'),

    #System Settings Page
    path('System-Settings/', System_Settings.as_view(),name="System_Settings"),


    #User List URL
    path('User/', UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/edit/', UserEditView.as_view(), name='user_edit'),
    path('users/<int:user_id>/update/', UserEditView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('user/<int:pk>/toggle-status/', ToggleUserStatusView.as_view(), name='user_toggle_status'),

    #User Profile
    path('user_profile/',UserProfileView.as_view(),name='user_profile'),
    path('edit_profile/', UserUpdateProfileView.as_view(), name='edit_profile'),


    
    #User Role URL
    path('roles/', RoleListView.as_view(), name='role_list'),
    path('roles/create/', RoleCreateView.as_view(), name='role_create'),
    path('roles/update/<int:pk>/', RoleUpdateView.as_view(), name='role_update'),
    path('roles/delete/<int:pk>/', RoleDeleteView.as_view(), name='role_delete'),

    
    #Category List URL
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/update/<int:pk>/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/delete/<int:pk>/', CategoryDeleteView.as_view(), name='category_delete'),


    #Gender Role URL
    path('gender/', GenderListView.as_view(), name='gender_list'),
    path('gender/create/', GenderCreateView.as_view(), name='gender_create'),
    path('gender/update/<int:pk>/', GenderUpdateView.as_view(), name='gender_update'),
    path('gender/delete/<int:pk>/', GenderDeleteView.as_view(), name='gender_delete'),


    # GameType URL
    path('gametype/', GameTypeListView.as_view(), name='gametype_list'),
    path('gametype/create/', GameTypeCreateView.as_view(), name='gametype_create'),
    path('gametype/update/<int:pk>/', GameTypeUpdateView.as_view(), name='gametype_update'),
    path('gametype/delete/<int:pk>/', GameTypeDeleteView.as_view(), name='gametype_delete'),

    # FieldCapacity URL
    path('fieldcapacity/', FieldCapacityListView.as_view(), name='fieldcapacity_list'),
    path('fieldcapacity/create/', FieldCapacityCreateView.as_view(), name='fieldcapacity_create'),
    path('fieldcapacity/update/<int:pk>/', FieldCapacityUpdateView.as_view(), name='fieldcapacity_update'),
    path('fieldcapacity/delete/<int:pk>/', FieldCapacityDeleteView.as_view(), name='fieldcapacity_delete'),

    # Ground Materials URL
    path('groundmaterial/', GroundMaterialListView.as_view(), name='groundmaterial_list'),
    path('groundmaterial/create/', GroundMaterialCreateView.as_view(), name='groundmaterial_create'),
    path('groundmaterial/update/<int:pk>/', GroundMaterialUpdateView.as_view(), name='groundmaterial_update'),
    path('groundmaterial/delete/<int:pk>/', GroundMaterialDeleteView.as_view(), name='groundmaterial_delete'),

    # Tournament Style URL
    path('tournamentstyle/', TournamentStyleListView.as_view(), name='tournamentstyle_list'),
    path('tournamentstyle/create/', TournamentStyleCreateView.as_view(), name='tournamentstyle_create'),
    path('tournamentstyle/update/<int:pk>/', TournamentStyleUpdateView.as_view(), name='tournamentstyle_update'),
    path('tournamentstyle/delete/<int:pk>/', TournamentStyleDeleteView.as_view(), name='tournamentstyle_delete'),

    # Event Type URL
    path('eventtype/', EventTypeListView.as_view(), name='eventtype_list'),
    path('eventtype/create/', EventTypeCreateView.as_view(), name='eventtype_create'),
    path('eventtype/update/<int:pk>/', EventTypeUpdateView.as_view(), name='eventtype_update'),
    path('eventtype/delete/<int:pk>/', EventTypeDeleteView.as_view(), name='eventtype_delete'),

]



