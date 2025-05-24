from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='update_profile'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('profile/reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
]