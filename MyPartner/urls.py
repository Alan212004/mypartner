from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from users.views import (
    CustomPasswordResetView, send_interest, accept_interest, decline_interest, notifications, 
    mark_as_read, my_profile, not_interested, home, register, 
    profile_detail, edit_profile, delete_image, forgot_username, 
    upload_images, admin_dashboard, admin_profiles, admin_users, 
    admin_statistics, admin_notifications, update_is_verified, update_needs_verification,
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
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
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
    path('admin/', admin.site.urls),  # Django's default admin site
    path('admin-panel/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/profiles/', admin_profiles, name='admin_profiles'),
    path('admin-panel/users/', admin_users, name='admin_users'),
    path('admin-panel/statistics/', admin_statistics, name='admin_statistics'),
    path('admin-panel/notifications/', admin_notifications, name='admin_notifications'),

    path('update_is_verified/<int:user_id>/', update_is_verified, name='update_is_verified'),
    path('update_needs_verification/<int:user_id>/', update_needs_verification, name='update_needs_verification'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
