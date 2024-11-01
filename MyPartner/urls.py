from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from users.views import (
    send_interest, accept_interest, decline_interest, notifications, 
    mark_as_read, my_profile, not_interested, home, register, 
    profile_detail, edit_profile, delete_image, forgot_username, 
    upload_images, admin_dashboard, admin_profiles, admin_users, 
    admin_statistics, admin_notifications
)

urlpatterns = [
    # Home page
    path('', home, name='home'),

    # User registration and authentication
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # User profile management
    path('my_profile/', my_profile, name='my_profile'),
    path('profile/<str:username>/', profile_detail, name='profile_detail'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('delete_image/<int:image_id>/', delete_image, name='delete_image'),

    # Password reset views
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Additional user functionality
    path('forgot-username/', forgot_username, name='forgot_username'),
    path('upload_images/', upload_images, name='upload_images'),

    

    # Interest and notification handling
    path('send_interest/<int:profile_id>/', send_interest, name='send_interest'),
    path('not-interested/<int:notification_id>/', not_interested, name='not_interested'),
    path('notifications/', notifications, name='notifications'),
    path('accept-interest/<int:notification_id>/', accept_interest, name='accept_interest'),
    path('decline-interest/<int:notification_id>/', decline_interest, name='decline_interest'),
    path('mark_as_read/<int:notification_id>/', mark_as_read, name='mark_as_read'),

    # Admin Dashboard, Profiles, Users, Statistics, and Notifications
    # Admin site
    path('admin/', admin.site.urls),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/profiles/', admin_profiles, name='admin_profiles'),  # Add this line
    path('admin/users/', admin_users, name='admin_users'),            # Add this line
    path('admin/statistics/', admin_statistics, name='admin_statistics'),  # Add this line
    path('admin/notifications/', admin_notifications, name='admin_notifications'),  # Add this line

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
