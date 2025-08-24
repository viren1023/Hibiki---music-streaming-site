import re
from django import forms
from .models import User
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "password": forms.PasswordInput(),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already taken")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered")
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get("password")
        
        if not re.search(r"^(?=.*[0-9])(?=.*[!@#$%^&*]).{6,}$", password):
            raise ValidationError("Password must be at least 6 characters, include a number & a special char")
        
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match")

        return confirm_password
