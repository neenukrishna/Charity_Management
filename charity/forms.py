from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

# User Registration Form
class CustomUserForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=[('donor', 'Donor'), ('beneficiary', 'Beneficiary')])

    class Meta:
        model = CustomUser
        fields = ['fullname', 'email','phone','dob','place','post','pin','district','gender', 'password1', 'password2', 'user_type']

# User Login Form
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
