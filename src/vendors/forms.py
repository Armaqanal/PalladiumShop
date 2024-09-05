from .models import Vendor, Company
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm


class DateInput(forms.DateInput):
    input_type = 'date'


class OwnerRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=100, required=True,
                                   widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    company_address = forms.CharField(max_length=200, required=True,
                                      widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))

    class Meta:
        model = Vendor
        fields = ['username', 'email', 'phone', 'password1', 'password2', 'first_name', 'last_name', 'gender',
                  'photo', 'date_of_birth']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            css_class = 'form-control form-control-lg' if field != 'gender' else 'form-select'
            self.fields[field].widget.attrs.update({'class': css_class})
        self.fields['photo'].widget.attrs.update({'class': 'form-control'})  # Custom styling for the 'photo' field

    def clean_username(self):
        username = self.cleaned_data['username']
        phone = self.cleaned_data.get('phone')
        email = self.cleaned_data.get('email')
        if not (username or email or phone):
            raise ValidationError("Providing username, email, or phone number is required.", code='invalid')
        return username

    def save(self, commit=True):
        vendor = super().save(commit=False)
        vendor.role = Vendor.Roles.OWNER
        if commit:
            company_name = self.cleaned_data.get('company_name')
            company_address = self.cleaned_data.get('company_address')
            company = Company.objects.create(
                name=company_name,
                address=company_address
            )
            vendor.company = company
            vendor.save()
        return vendor

    class Meta:
        model = Vendor
        fields = ['username', 'email', 'phone', 'password1', 'password2', 'photo', 'first_name', 'last_name',
                  'date_of_birth', 'gender', 'company_name', 'company_address']
        widgets = {'date_of_birth': DateInput}


class CompanyCreationForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address']


class VendorsChangeForm(forms.ModelForm):
    company_name = forms.CharField(max_length=100, required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control' 'form-control-lg'}))
    company_address = forms.CharField(max_length=200, required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['gender'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['photo'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['date_of_birth'].widget.attrs.update({
            'class': 'form-control',
        })
        self.fields['company_name'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['company_address'].widget.attrs.update({
            'class': 'form-control'
        })

    class Meta:
        model = Vendor
        fields = ['email', 'phone', 'first_name', 'last_name', 'gender', 'photo', 'date_of_birth', 'company_name',
                  'company_address']
        widgets = {
            'date_of_birth': DateInput
        }

    def save(self, commit=True):
        vendor = super().save(commit=False)
        if commit:
            company = vendor.company
            company.name = self.cleaned_data.get('company_name')
            company.address = self.cleaned_data.get('company_address')
            company.save()
            vendor.save()
        return vendor
