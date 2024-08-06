from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm

from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from .models import Customer, Address

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'id': 'email'}),
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'id': 'password'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(request=self.request, email=email, password=password)
            if self.user_cache is None:
                raise ValidationError("Invalid email or password")
        return cleaned_data

    def get_user(self):
        return self.user_cache


class DateInput(forms.DateInput):
    input_type = 'date'


class CustomerRegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-lg'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control form-control-lg',
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control form-control-lg',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control form-control-lg',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control form-control-lg',
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'id': 'lastName'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'id': 'firstName'
        })
        self.fields['gender'].widget.attrs.update({
            'class': 'form-select',
        })
        self.fields['photo'].widget.attrs.update({
            'class': 'form-control ',
        })

        self.fields['date_of_birth'].widget.attrs.update({
            'class': 'form-control ',
        })
        # self.fields['date_of_birth'] = JalaliDateField(
        #     label='Date of Birth',
        #     widget=AdminJalaliDateWidget
        # )
        self.fields['address'].widget.attrs.update({
            'class': 'form-control ',
        })

    def clean_username(self):
        username = self.cleaned_data['username']
        phone = self.cleaned_data.get('phone')
        email = self.cleaned_data.get('email')
        if not (username or email or phone):
            raise ValidationError(
                "Providing username, email or phone number is required.",
                code='invalid'
            )
        return username

    class Meta:
        model = Customer
        fields = ['username', 'email', 'phone', 'password1', 'password2', 'photo', 'first_name', 'last_name',
                  'date_of_birth', 'gender', 'address']
        widgets = {
            'date_of_birth': DateInput
        }


class CustomerCreationForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ['email']


class CustomerChangeForm(UserChangeForm):
    class Meta:
        model = Customer
        fields = ['email']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'
