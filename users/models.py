from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date



class Profile(models.Model):
    RELIGION_CHOICES = [
        ('Hinduism', 'Hinduism'),
        ('Islam', 'Islam'),
        ('Christianity', 'Christianity'),
        ('Buddhism', 'Buddhism'),
        ('Sikhism', 'Sikhism'),
        ('Judaism', 'Judaism'),
        ('Atheism', 'Atheism'),
        ('Other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField(blank=True, null=True)  # Date of birth for automatic age calculation
    profile_photo = models.ImageField(upload_to='profile_pics', default='profile_pics/male_default.jpg')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    age = models.PositiveIntegerField(default=0, editable=False)  # Auto-calculated, not user-editable
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Male')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    
    # Location fields
    place = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    pin = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    education = models.CharField(max_length=100, blank=True, default='Degree')
    job = models.CharField(max_length=100, blank=True, null=True)
    religion = models.CharField(max_length=100, choices=RELIGION_CHOICES, blank=True, null=True)
    caste = models.CharField(max_length=100, blank=True, null=True)
    about_me = models.CharField(max_length=500, blank=True, null=True)

    # Family details
    family_background = models.CharField(max_length=10, choices=[('Lower', 'Lower'), ('Middle', 'Middle'), ('Upper', 'Upper')], default='Middle')
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    siblings_no = models.IntegerField(blank=True, null=True)
    father_job = models.CharField(max_length=100, blank=True, null=True)
    mother_job = models.CharField(max_length=100, blank=True, null=True)

    # Preferences
    preferred_age_min = models.IntegerField(default=18)
    preferred_age_max = models.IntegerField(default=35)
    preferred_religion = models.CharField(max_length=100, choices=RELIGION_CHOICES, blank=True, null=True)
    preferred_caste = models.CharField(max_length=100, blank=True, null=True)
    preferred_job = models.CharField(max_length=100, blank=True, null=True)
    preferred_family_background = models.CharField(max_length=10, choices=[('Lower', 'Lower'), ('Middle', 'Middle'), ('Upper', 'Upper')], default='Middle')

    # Social media
    facebook_id = models.CharField(max_length=200, blank=True, null=True)
    instagram_id = models.CharField(max_length=200, blank=True, null=True)
    twitter_id = models.CharField(max_length=200, blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    needs_verification = models.BooleanField(default=False)
    

    def clean(self):
        super().clean()
        if self.preferred_age_min > self.preferred_age_max:
            raise ValidationError("Preferred minimum age cannot be greater than maximum age.")

    def calculate_age(self):
        """Calculates age based on dob."""
        if self.dob:
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return 0

    def save(self, *args, **kwargs):
                
        if not self.profile_photo:
            self.profile_photo = 'profile_pics/female_default.png' if self.gender == 'Female' else 'profile_pics/male_default.jpg'
        
        # Set location
        location_parts = [self.place, self.city, self.state, self.country]
        self.location = ', '.join(filter(None, location_parts))
        
        # Calculate age if DOB is provided
        if self.dob:
            self.age = self.calculate_age()
        
        # Set default preferences based on gender
        if self.gender == 'Female' and self.age:
            self.preferred_age_min, self.preferred_age_max = self.age, self.age + 5
        elif self.gender == 'Male' and self.age:
            self.preferred_age_min, self.preferred_age_max = max(18, self.age - 5), self.age
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} Profile'



class ProfileImage(models.Model):
    profile = models.ForeignKey(Profile, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='additional_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)

    def clean(self):
     if self.image.size > 2 * 1024 * 1024:  # Limit to 2MB
        raise ValidationError("Image file too large ( > 2MB ).")
     super().clean()

    def __str__(self):
        return f"{self.profile.user.username}'s additional image"

class DeletedProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Deleted on {self.deleted_at}"

class NotificationType(models.TextChoices):
    INTEREST_REQUEST = 'interest_request', 'Interest Request'
    MESSAGE = 'message', 'Message'
    GENERAL = 'general', 'General'
    INTEREST_ACCEPTED = 'interest_accepted', 'Interest Accepted'  # Corrected
    INTEREST_DECLINED = 'interest_declined', 'Interest Declined'  # Corrected


class Notification(models.Model):
    sender = models.ForeignKey(Profile, related_name='sent_notifications', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Profile, related_name='received_notifications', on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices, default=NotificationType.INTEREST_REQUEST)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_unread_notifications(cls, profile):
        return cls.objects.filter(receiver=profile, is_read=False)
    
    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.message}"

class InterestRequest(models.Model):
    from_user = models.ForeignKey(Profile, related_name='sent_interest_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(Profile, related_name='received_interest_requests', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)  # Add this field
    created_at = models.DateTimeField(auto_now_add=True)

class Interest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_interests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_interests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"
    
