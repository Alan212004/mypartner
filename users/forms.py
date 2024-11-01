from django import forms
from .models import Profile, ProfileImage
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from datetime import date
# Form for updating user profile information
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['age']  # Exclude age since it will be calculated
        fields = [
            'first_name', 'last_name', 'email', 'dob', 'gender', 'phone_number', 'address', 'about_me',
            'place', 'city', 'state', 'country', 'pin',   # Include dob for age calculation
            'education', 'job', 'religion', 'caste', 'family_background',
            'siblings_no', 'father_name', 'mother_name', 'father_job', 'mother_job',
            'preferred_age_min', 'preferred_age_max', 'preferred_religion', 
            'preferred_caste', 'preferred_job', 'preferred_family_background', 
            'facebook_id', 'instagram_id', 'twitter_id', 'profile_photo'
        ]

    def clean(self):
        cleaned_data = super().clean()
        profile = self.instance

        # Check if name, gender, email, or dob has changed
        if (cleaned_data.get('first_name') != profile.first_name or
            cleaned_data.get('last_name') != profile.last_name or
            cleaned_data.get('email') != profile.email or
            cleaned_data.get('gender') != profile.gender or
            cleaned_data.get('dob') != profile.dob):  # Check if dob has changed
            profile.needs_verification = True  # Set flag for verification

        return cleaned_data

# Search form for finding profiles based on criteria
class SearchForm(forms.Form):
    age_min = forms.IntegerField(required=False)
    age_max = forms.IntegerField(required=False)
    location = forms.CharField(max_length=100, required=False)
    religion = forms.CharField(max_length=100, required=False)
    caste = forms.CharField(max_length=100, required=False)

# User registration form including additional fields
class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'date_of_birth',
            'gender', 'phone_number', 'password1', 'password2', 'profile_photo'
        )

    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        age = (date.today() - dob).days // 365
        if age < 20:
            raise forms.ValidationError("You must be at least 20 years old to register.")
        return dob

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not phone_number.isdigit() or len(phone_number) < 10:
            raise forms.ValidationError("Enter a valid phone number.")
        return phone_number

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


# Form for requesting a username reset
class UsernameRequestForm(forms.Form):
    email = forms.EmailField(label='Email Address')

# User login form
class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
                'style': 'text-transform: none;',
                'autocomplete': 'off',          # Disable autocomplete
                'autocapitalize': 'none',       # Disable capitalization on mobile devices
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password',
                'style': 'text-transform: none;',
                'autocomplete': 'off',
                'autocapitalize': 'none',
            }),
        }


# Form for managing additional images
class AdditionalImagesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(5):
            self.fields[f'image_{i}'] = forms.ImageField(required=False)


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = ProfileImage
        fields = ['image'] 


   