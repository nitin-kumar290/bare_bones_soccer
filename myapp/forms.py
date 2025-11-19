from django import forms
from .models import Person, PlayerProfile
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from .models import PlayerProfile, EventRSVP
import re
from datetime import date

# DELETE LATER
# class SportsStableForm(forms.ModelForm):
#     class Meta:
#         model = SportsStable
#         fields = ['full_name', 'email', 'phone', 'dob', 
#             'emergency_contact_name', 'emergency_contact_phone', 
#             'electronic_signature', 'agree_to_waiver']  # match your model fields
#         widgets = {
#             'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
#             'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (optional)'}),
#             'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact Name'}),
#             'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact Phone'}),
#             'electronic_signature': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type Your Name as Signature'}),
#             'agree_to_waiver': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any additional info', 'rows': 4}),
#         }

class ForgotUsernameForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'you@example.com'}),
    )


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'email', 'message']
        widgets =  {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5}),
        }


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'})
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Don't clear password fields on validation errors
        self.fields['password'].widget.render_value = True
        self.fields['confirm_password'].widget.render_value = True

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
        }


    def clean_username(self):
        # Get the username from the form data
        username = self.cleaned_data.get("username", "")
        # Convert the username to lowercase
        return username.lower()

    
    def clean_email(self):
            email = self.cleaned_data.get("email", "").lower()
            # Check for existing users with the same email (case-insensitive).
            if User.objects.filter(email=email).exists():
                raise ValidationError("An account with this email already exists.")
            return email
    
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")


class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'})
    )



class PlayerProfileForm(forms.ModelForm):
    age_category = forms.ChoiceField(
        choices=[('adult', 'Adult (18+)'), ('minor', 'Minor (Under 18)')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
        label='Age Category'
    )
    # Override the fields with specific widgets and validation
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '(123) 456-7890','required': 'required', 'class': 'form-control'}),
        max_length=15,
        required=True,
        label='Phone'
    )
    dob = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'max': date.today().strftime('%Y-%m-%d'),  # Prevents future dates
            'required': 'required',
            'class': 'form-control'
        }),
        required=False,
        label='Date of Birth'
    )
    emergency_contact_name = forms.CharField(required=True)

    emergency_contact_phone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '(123) 456-7890','required': 'required', 'class': 'form-control'}),
        max_length=15,
        required=True,
        label='Emergency Contact Phone'
    )
    marketing_opt_in = forms.BooleanField(
        initial=True,  # This makes it checked by default
        required=False,  # This allows unchecking
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
                   }
        )
    )
    electronic_signature = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Type Your Name as Signature', 'required': 'required', 'class': 'form-control'}))
    agree_to_waiver = forms.BooleanField(required=True)

    class Meta:
        model = PlayerProfile
        fields = [
            'full_name', 'phone', 'dob', 'age_category',
            'emergency_contact_name', 'emergency_contact_phone',
            'electronic_signature', 'agree_to_waiver', 'marketing_opt_in'
        ]

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Remove all non-numeric characters
        phone_digits = re.sub(r'\D', '', phone)
        
        if len(phone_digits) != 10:
            raise forms.ValidationError('Please enter a valid 10-digit phone number.')
        
        # Format the phone number as (XXX) XXX-XXXX
        formatted_phone = f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
        return formatted_phone

    def clean_emergency_contact_phone(self):
        phone = self.cleaned_data.get('emergency_contact_phone')
        # Use the same validation as primary phone
        phone_digits = re.sub(r'\D', '', phone)
        
        if len(phone_digits) != 10:
            raise forms.ValidationError('Please enter a valid 10-digit phone number.')
        
        formatted_phone = f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
        return formatted_phone

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        today = date.today()
        
        if dob:
            if dob > today:
                raise forms.ValidationError('Date of birth cannot be in the future.')
        
        return dob


class UnsubscribeForm(forms.Form):
    email = forms.EmailField(label="Email Address")
    
    # Define the same choices as in the model
    REASON_CHOICES = [
        ('too_many', 'I receive too many emails'),
        ('not_relevant', 'Content is not relevant to me'),
        ('never_signed_up', 'I never signed up for these emails'),
        ('other', 'Other reason')
    ]
    
    reason = forms.ChoiceField(
        choices=REASON_CHOICES,
        widget=forms.RadioSelect,
        label="Reason for unsubscribing",
        required=True
    )
    
    other_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label="If 'Other', please specify"
    )


class EventRSVPForm(forms.ModelForm):
    class Meta:
        model = EventRSVP
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your email'
            }),
        }
