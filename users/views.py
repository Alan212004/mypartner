from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import (AdditionalImagesForm, ProfileUpdateForm, 
                    SearchForm, UserLoginForm, UserRegistrationForm, 
                    ProfileImageForm, UsernameRequestForm)
from .models import Profile, ProfileImage, InterestRequest, Notification
from .models import Profile, Interest
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from datetime import date, datetime
from django.utils import timezone
from django.db import transaction
from django.urls import reverse
from .models import Notification, Interest, NotificationType
from django.http import JsonResponse

@property
def unread_notifications_count(self):
    return self.received_notifications.filter(is_read=False).count()

@login_required
def my_profile(request):
    user = request.user  # Get the currently logged-in user
    profile = get_object_or_404(Profile, user=user)  # Get the Profile instance
    images = ProfileImage.objects.filter(profile=profile)  # Get associated images
    context = {'profile': profile, 'images': images}
    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    existing_images = ProfileImage.objects.filter(profile=profile)

    if request.method == 'POST':
        print("POST request received.")
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if profile_form.is_valid():
            print("Profile form is valid.")
            updated_profile = profile_form.save(commit=False)
            new_age = calculate_age(updated_profile.dob)

            # Check if any relevant fields have changed to set needs_verification
            if (profile_form.cleaned_data['first_name'] != profile.first_name or
                profile_form.cleaned_data['last_name'] != profile.last_name or
                profile_form.cleaned_data['email'] != profile.email or
                profile_form.cleaned_data['gender'] != profile.gender or
                new_age != profile.age):  # Check for age change
                profile.needs_verification = True  # Set the flag to require verification
                profile.is_verified = False  # Set verified status to False

            # Save the profile with the new data
            updated_profile.age = new_age  # Update the age
            updated_profile.is_verified = profile.is_verified  # Maintain verification status
            updated_profile.needs_verification = profile.needs_verification
            updated_profile.save()

            # Handle additional images (limited to 5 total)
            # Handle additional images (limited to 5 total)
            total_images = existing_images.count()
            for i in range(5):
                 if total_images < 5:  # Only allow new uploads if total images are less than 5
                     image = request.FILES.get(f'image_{i}')
                     if image:
                        ProfileImage.objects.create(profile=profile, image=image)
                        total_images += 1  # Increment the count
                     else:
                        break  # Exit loop if no more images are uploaded


            # Handle deletion of additional images based on checked checkboxes
            for existing_image in existing_images:
                delete_checkbox = request.POST.get(f'delete_image_{existing_image.id}')
                if delete_checkbox:  # If the checkbox is checked
                    existing_image.delete()  # Delete the image
                    messages.success(request, 'Your additional image was deleted successfully.')

            messages.success(request, 'Profile updated successfully! Please note that some changes require verification.')
            return redirect('my_profile')  # Redirect back to the profile page
        else:
            print("Profile form errors:", profile_form.errors)

    else:
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        'profile_form': profile_form,
        'existing_images': existing_images,
        'range': range(5),
    }
    return render(request, 'edit_profile.html', context)

@login_required
def delete_image(request, image_id):
    image = get_object_or_404(ProfileImage, id=image_id)
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted successfully.')
        return redirect('edit_profile')  # Ensure this URL is correct in your URLconf

    return render(request, 'confirm_delete.html', {'image': image})  # Add confirmation template



@login_required
def home(request):
    # Default value for unread notifications
    unread_notifications_count = 0  

    if request.user.is_authenticated:
        current_user = request.user
        
        # Check if the user is an admin
        if current_user.is_superuser:
            # Fetch all verified profiles for admin
            profiles = Profile.objects.all().exclude(user=current_user)
        else:
            # Fetch all verified profiles for regular users
            profiles = Profile.objects.filter(is_verified=True).exclude(user=current_user)

            # Try to fetch the current user's profile
            try:
                current_user_profile = current_user.profile
                gender = current_user_profile.gender.capitalize()
                opposite_gender = 'Female' if gender == 'Male' else 'Male'
                age = current_user_profile.age
                
                # Determine age range based on the user's preferences
                min_age = current_user_profile.preferred_age_min or (age - 5)
                max_age = current_user_profile.preferred_age_max or (age + 5)

            except Profile.DoesNotExist:
                # Redirect to a profile creation page if the profile doesn't exist
                return redirect('profile_creation')

            # Filter profiles based on the opposite gender and age range
            profiles = profiles.filter(
                gender=opposite_gender, age__gte=min_age, age__lte=max_age
            ).exclude(user=request.user)

        # Optionally filter profiles by user's preferences
        religion_profiles = profiles.filter(religion=current_user_profile.religion) if not current_user.is_superuser else profiles
        preferred_religion_profiles = profiles.filter(religion=current_user_profile.preferred_religion) if not current_user.is_superuser else profiles
        caste_profiles = profiles.filter(caste=current_user_profile.caste) if not current_user.is_superuser else profiles
        preferred_caste_profiles = profiles.filter(caste=current_user_profile.preferred_caste) if not current_user.is_superuser else profiles
        job_profiles = profiles.filter(job=current_user_profile.job) if not current_user.is_superuser else profiles
        preferred_job_profiles = profiles.filter(job=current_user_profile.preferred_job) if not current_user.is_superuser else profiles
        family_background_profiles = profiles.filter(family_background=current_user_profile.family_background) if not current_user.is_superuser else profiles
        preferred_family_background_profiles = profiles.filter(family_background=current_user_profile.preferred_family_background) if not current_user.is_superuser else profiles

        # Count unread notifications
        if not current_user.is_superuser:
            unread_notifications_count = current_user_profile.received_notifications.filter(is_read=False).count()

    # Prepare the context for rendering
    context = {
        'profiles': profiles,
        'religion_profiles': religion_profiles,
        'preferred_religion_profiles': preferred_religion_profiles,
        'job_profiles': job_profiles,
        'preferred_job_profiles': preferred_job_profiles,
        'caste_profiles': caste_profiles,
        'preferred_caste_profiles': preferred_caste_profiles,
        'family_background_profiles': family_background_profiles,
        'preferred_family_background_profiles': preferred_family_background_profiles,
        'has_profiles': profiles.exists(),
        'has_religion_profiles': religion_profiles.exists(),
        'has_preferred_religion_profiles': preferred_religion_profiles.exists(),
        'has_job_profiles': job_profiles.exists(),
        'has_preferred_job_profiles': preferred_job_profiles.exists(),
        'has_caste_profiles': caste_profiles.exists(),
        'has_preferred_caste_profiles': preferred_caste_profiles.exists(),
        'has_family_background_profiles': family_background_profiles.exists(),
        'has_preferred_family_background_profiles': preferred_family_background_profiles.exists(),
        'unread_notifications_count': unread_notifications_count,
    }

    # Render the home page with context
    return render(request, 'home.html', context)



@transaction.atomic
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the User instance from the form
                user = form.save()

                # Check if a profile already exists for the user
                profile, created = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'first_name': form.cleaned_data['first_name'],
                        'last_name': form.cleaned_data['last_name'],
                        'email': form.cleaned_data['email'],
                        'dob': form.cleaned_data['date_of_birth'],
                        'gender': form.cleaned_data['gender'],
                        'phone_number': form.cleaned_data['phone_number'],
                        'profile_photo': form.cleaned_data.get('profile_photo'),
                    }
                )

                if not created:
                    messages.warning(request, 'A profile already exists for this user. The profile has not been updated.')

                # Calculate age based on the date of birth
                profile.age = calculate_age(form.cleaned_data['date_of_birth'])
                profile.save()  # Save the profile with the calculated age

                # Log the user in and redirect to home
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect('home')  # Redirect to home page

            except IntegrityError as e:
                # Log the error for debugging
                print(f'IntegrityError: {e}')  # Output to console for debugging
                messages.error(request, 'An account with similar details already exists. Please try again.')

    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def calculate_age(dob):
    """Calculate age from date of birth."""
    today = timezone.now().date()
    if dob:
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return 0  # Return 0 if dob is None

def filter_profiles_by_preferences(profiles, current_user_profile, opposite_gender, min_age, max_age):
    return profiles.filter(
        gender=opposite_gender,
        age__gte=min_age,
        age__lte=max_age,
        religion=current_user_profile.religion,
        caste=current_user_profile.caste,
        job=current_user_profile.job,
        family_background=current_user_profile.family_background,
    ).exclude(user=current_user_profile.user)

def search(request):
    profiles = Profile.objects.all()
    search_form = SearchForm(request.GET)

    if search_form.is_valid():
        query = Q()
        age_min = search_form.cleaned_data.get('age_min')
        age_max = search_form.cleaned_data.get('age_max')
        location = search_form.cleaned_data.get('location')
        religion = search_form.cleaned_data.get('religion')
        caste = search_form.cleaned_data.get('caste')

        if age_min:
            query &= Q(age__gte=age_min)
        if age_max:
            query &= Q(age__lte=age_max)
        if location:
            query &= Q(location__icontains=location)
        if religion:
            query &= Q(religion__icontains=religion)
        if caste:
            query &= Q(caste__icontains=caste)

        profiles = profiles.filter(query)

    context = {'profiles': profiles, 'search_form': search_form}
    return render(request, 'search_results.html', context)

@login_required
def match_suggestions(request):
    user_profile = request.user.profile
    suggested_profiles = Profile.objects.select_related('user').all()


    if user_profile.preferred_age_min and user_profile.preferred_age_max:
        suggested_profiles = suggested_profiles.filter(
            age__gte=user_profile.preferred_age_min,
            age__lte=user_profile.preferred_age_max
        )

    if user_profile.preferred_religion:
        suggested_profiles = suggested_profiles.filter(religion__iexact=user_profile.preferred_religion)

    if user_profile.preferred_caste:
        suggested_profiles = suggested_profiles.filter(caste__iexact=user_profile.preferred_caste)

    suggested_profiles = suggested_profiles.order_by('age')

    context = {'suggested_profiles': suggested_profiles}
    return render(request, 'match_suggestions.html', context)

def forgot_username(request):
    if request.method == 'POST':
        form = UsernameRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                send_mail(
                    'Your Username',
                    f'Your username is {user.username}.',
                    'from@example.com',  # Use settings.EMAIL_HOST_USER
                    [email],
                    fail_silently=False,
                )
                return render(request, 'username_sent.html')  # Inform the user
            except User.DoesNotExist:
                form.add_error('email', 'No user with this email exists.')
    else:
        form = UsernameRequestForm()
    
    return render(request, 'forgot_username.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('my_profile')  # Change to your desired redirect
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def profile_detail(request, username):
    # Fetch the user based on the username
    user = get_object_or_404(User, username=username)  # Correctly fetch the User instance
    
    # Fetch the profile based on the User instance
    profile = get_object_or_404(Profile, user=user)  # Use the User instance

    # Check for existing interest requests and statuses
    interest_requested = Interest.objects.filter(sender=request.user, receiver=profile.user).exists()
    interest_accepted = Interest.objects.filter(sender=profile.user, receiver=request.user).filter(status='accepted').exists()
    interest_declined = Interest.objects.filter(sender=profile.user, receiver=request.user).filter(status='declined').exists()

    # Fetch the notification ID if the request was made
    notification_id = None
    if interest_requested:
        notification = Notification.objects.filter(sender=request.user.profile, receiver=profile).first()
        if notification:
            notification_id = notification.id

    # Only create a notification if the user is not viewing their own profile and is not an admin
    if request.user != profile.user and not request.user.is_staff:
        Notification.objects.create(
            sender=request.user.profile,
            receiver=profile,
            message="viewed your profile",
            notification_type=NotificationType.GENERAL
        )

    # Gather additional images related to the profile
    additional_images = ProfileImage.objects.filter(profile=profile)

    # Prepare the context for rendering
    context = {
        'profile': profile,
        'additional_images': additional_images,
        'interest_requested': interest_requested,
        'interest_accepted': interest_accepted,
        'interest_declined': interest_declined,
        'notification_id': notification_id,
    }
    
    return render(request, 'profile_detail.html', context)  # Render the profile detail template


@login_required
def upload_images(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES)

        if form.is_valid():
            images = request.FILES.getlist('additional_images')
            for img in images:
                ProfileImage.objects.create(profile=profile, image=img)

            messages.success(request, 'Images uploaded successfully!')
            return redirect('my_profile')  # Redirect to a relevant view

    else:
        form = ProfileImageForm()

    context = {'form': form}
    return render(request, 'upload_images.html', context)


@login_required
def notifications(request):
    # Get the current user's profile
    current_user_profile = request.user.profile
    
    # Fetch all notifications related to the current user's profile
    notifications = current_user_profile.received_notifications.all().order_by('-created_at')  # Assuming you have a 'created_at' field

    # Optionally mark notifications as read
    unread_notifications = notifications.filter(is_read=False)
    if unread_notifications.exists():
        unread_notifications.update(is_read=True)

    context = {
        'notifications': notifications,
        'unread_count': unread_notifications.count(),  # Count of unread notifications
    }
    
    return render(request, 'notifications.html', context)


@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, receiver=request.user.profile)
    notification.is_read = True
    notification.save()
    messages.success(request, 'Notification marked as read!')
    return redirect('notifications')

@login_required
def mark_all_as_read(request):
    request.user.profile.received_notifications.update(is_read=True)
    messages.success(request, "All notifications marked as read!")
    return redirect('notifications')


@login_required
def send_interest_request(from_user_id, to_user_id):
    try:
        from_user_profile = Profile.objects.get(user_id=from_user_id)
        to_user_profile = Profile.objects.get(user_id=to_user_id)

        # Check if an interest request already exists
        if Interest.objects.filter(sender=from_user_profile.user, receiver=to_user_profile.user).exists():
            print("Interest request already sent.")
            return False  # Indicate failure

        interest_request = InterestRequest(
            from_user=from_user_profile,
            to_user=to_user_profile,
            is_accepted=False,
            is_declined=False,
        )
        interest_request.save()

        Notification.objects.create(
            receiver=to_user_profile,
            message=f"{from_user_profile.user.username} has expressed interest in your profile.",
            is_read=False
        )

        return True  # Indicate success
    except Profile.DoesNotExist:
        print("One of the profiles does not exist.")
        return False  # Indicate failure

########################

@login_required
def accept_interest(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    
    try:
        with transaction.atomic():
            # Update or create the interest
            interest, created = Interest.objects.get_or_create(
                sender=notification.sender,  
                receiver=notification.receiver,
                defaults={'status': 'accepted'}
            )

            # If the interest was already created, update its status
            if not created:
                interest.status = 'accepted'
                interest.save()

            # Mark the notification as read
            notification.is_read = True
            notification.save()

            # Send a success response
            return JsonResponse({'status': 'accepted'})
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred while accepting the interest.'}, status=500)


@login_required
def decline_interest(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    try:
        with transaction.atomic():
            # Ensure the interest exists before trying to delete
            interest = Interest.objects.get(sender=notification.sender.user, receiver=notification.receiver.user)
            interest.delete()

            # Create a notification for the sender
            Notification.objects.create(
                sender=request.user.profile,
                receiver=notification.sender,
                message=f"{request.user.first_name} has declined your interest request.",
                notification_type=NotificationType.INTEREST_DECLINED,
            )

            notification.is_read = True
            notification.save()

            return JsonResponse({'status': 'declined'})
    except Interest.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Interest request not found.'}, status=404)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred while declining the interest.'}, status=500)



@login_required
def send_interest(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, id=profile_id)

        if profile.user == request.user:
            messages.error(request, "You cannot send an interest request to yourself.")
            return redirect('profile_detail', username=profile.user.username)

        try:
            with transaction.atomic():
                # Create or update the interest record
                Interest.objects.update_or_create(
                    sender=request.user,
                    receiver=profile.user,
                    defaults={'status': 'pending'}
                )

                # Create a notification for the receiver
                Notification.objects.create(
                    sender=request.user.profile,
                    receiver=profile,
                    message=f"{request.user.username} has sent you an interest request.",
                    notification_type=NotificationType.INTEREST_REQUEST
                )

                messages.success(request, "Interest request sent successfully.")
                return redirect('profile_detail', username=profile.user.username)
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    
    return redirect('profile_detail', username=profile.user.username)


def not_interested(request, notification_id):
    if request.method == 'POST':
        try:
            interest_request = get_object_or_404(InterestRequest, id=notification_id, receiver=request.user.profile)
            interest_request.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error'}, status=400)

# # # # # # # # # ## # ##
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_dashboard(request):
    total_profiles = Profile.objects.count()
    total_notifications = Notification.objects.count()
    total_interests = Interest.objects.count()
    verified_profiles = Profile.objects.filter(is_verified=True).count()

    context = {
        'total_profiles': total_profiles,
        'total_notifications': total_notifications,
        'total_interests': total_interests,
        'verified_profiles': verified_profiles,
    }
    
    return render(request, 'admin_dashboard.html', context)

@staff_member_required
def admin_profiles(request):
    profiles = Profile.objects.all()  # Fetch all user profiles for admin
    return render(request, 'admin_profiles.html', {'profiles': profiles})

@staff_member_required
def admin_users(request):
    users = User.objects.all()  # Fetch all users
    return render(request, 'admin_users.html', {'users': users})

@staff_member_required
def admin_statistics(request):
    total_profiles = Profile.objects.count()
    total_notifications = Notification.objects.count()
    total_interests = Interest.objects.count()

    context = {
        'total_profiles': total_profiles,
        'total_notifications': total_notifications,
        'total_interests': total_interests,
    }
    
    return render(request, 'admin_statistics.html', context)

@staff_member_required
def admin_notifications(request):
    notifications = Notification.objects.all()  # Fetch all notifications

    context = {
        'notifications': notifications,
    }
    
    return render(request, 'admin_notifications.html', context)