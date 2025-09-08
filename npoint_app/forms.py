from django import forms
from .models import UserProfile, JSONData
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

# class UserProfileCreationForm(UserCreationForm):
#     class Meta:
#         model = UserProfile
#         fields = ('username', 'email', 'password1', 'password2')

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if UserProfile.objects.filter(email=email).exists():
#             raise ValidationError("Email already exists")
#         return email
#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         if UserProfile.objects.filter(username=username).exists():
#             raise ValidationError("Username already exists")
#         return username
    
User = get_user_model()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User                      # << use auth user model
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # match your login pane’s "input" style
        self.fields["username"].widget.attrs.update({"class": "input", "placeholder": "Username"})
        self.fields["email"].widget.attrs.update({"class": "input", "placeholder": "Email"})
        self.fields["password1"].widget.attrs.update({"class": "input", "placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"class": "input", "placeholder": "Confirm Password"})
        # optional:
        for f in self.fields.values():
            f.help_text = ""  # hide default help_text

class JsonDataForm(forms.ModelForm):
    class Meta:
        model = JSONData
        fields = ['title', 'description', 'json_picture', 'json_content', 'is_public']

    
