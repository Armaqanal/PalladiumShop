from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from customers.models import Customer, Address, User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


class PalladiumUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone', 'is_staff', 'is_superuser', 'get_date_joined',
                    'get_date_modified', 'get_date_of_birth']
    list_filter = ['username', 'email']
    readonly_fields = ['last_login', 'get_date_joined', 'get_date_modified']

    fieldsets = [
        (None, {
            "fields": ("username", "email", "phone", "password")
        }),
        ('Personal Info', {
            "fields": ["first_name", "last_name",  "gender", "date_of_birth", "photo",
                       "get_date_modified", "last_login"]
        }),
        ("Permissions", {
            "fields": ("is_superuser", "is_staff", "is_active", "groups", "user_permissions")
        }),
    ]

    add_fieldsets = [
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "phone", "password1", "password2")
        }),
        ('Personal Info', {
            "fields": ["first_name", "last_name",  "gender", "date_of_birth", "photo",
                       "get_date_modified", "last_login"]
        }),
        ("Permissions", {
            "fields": ("is_superuser", "is_staff", "is_active", "groups", "user_permissions")
        }),
    ]

    search_fields = ("email",)
    ordering = ("email",)

    @admin.display(description=_('Date Joined'))
    def get_date_joined(self, obj):
        return obj.date_joined.strftime('%a, %d %b %Y %H:%M:%S')

    @admin.display(description=_('Date Modified'))
    def get_date_modified(self, obj):
        return obj.date_modified.strftime('%a, %d %b %Y %H:%M:%S')

    @admin.display(description=_('Date of Birth'))
    def get_date_of_birth(self, obj):
        if obj.date_of_birth:
            return obj.date_of_birth.strftime('%Y-%m-%d')
        return "N/A"


admin.site.register(User, PalladiumUserAdmin)


class CustomerAdmin(PalladiumUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = Customer

    fieldsets = (
        (None, {
            "fields": ("username", "email", "phone", "password")
        }),
        ('Personal Info', {
            "fields": ("first_name", "last_name", "gender", "date_of_birth", "photo")
        }),
        ("Permissions", {
            "fields": ("is_superuser", "is_staff", "is_active", "groups", "user_permissions")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "phone", "password1", "password2")
        }),
        ('Personal Info', {
            "fields": ("first_name", "last_name", "gender", "date_of_birth", "photo")
        }),

        ("Permissions", {
            "fields": ("is_superuser", "is_staff", "is_active", "groups", "user_permissions")
        }),
    )

    readonly_fields = ('date_joined', 'date_modified', 'last_login')

    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(Customer, CustomerAdmin)


class AddressAdmin(admin.ModelAdmin):
    list_display = ('zip_code', 'street', 'city', 'state')
    list_filter = ('city',)


admin.site.register(Address, AddressAdmin)
