from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import StudentProfile


class StudentRegisterForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=150, required=True, label="Full Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'})
    )
    age = forms.IntegerField(
        required=True, min_value=1, label="Age",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your age'})
    )
    status = forms.ChoiceField(
        choices=StudentProfile.STATUS_CHOICES, required=True, label="You are a",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'age', 'status', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Choose a username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            StudentProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                age=self.cleaned_data['age'],
                status=self.cleaned_data['status'],
            )
        return user


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your password'})
