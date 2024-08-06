from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from customers.models import Customer, Address, User
from jalali_date import datetime2jalali
from jalali_date.admin import ModelAdminJalaliMixin
from django.contrib.auth.admin import UserAdmin


class PalladiumUserAdmin(ModelAdminJalaliMixin, UserAdmin):
    list_display = ['username', 'email', 'phone', 'is_staff', 'is_superuser', 'get_date_joined_jalali',
                    'get_date_modified_jalali']
    list_filter = ['username', 'email']
    readonly_fields = ['last_login', 'get_date_joined_jalali', 'get_date_modified_jalali']

    fieldsets = [
        (None, {
            "fields": ("username", "email", "phone", "password")
        }),
        ('Personal Info', {
            "fields": ["first_name", "last_name", "address", "gender", "date_of_birth", "photo", "date_joined",
                       "get_date_modified_jalali", "last_login"]
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
            "fields": ["first_name", "last_name", "address", "gender", "date_of_birth", "photo", "date_joined",
                       "get_date_modified_jalali", "last_login"]
        }),
        ("Permissions", {
            "fields": ("is_superuser", "is_staff", "is_active", "groups", "user_permissions")
        }),
    ]

    search_fields = ("email",)
    ordering = ("email",)

    @admin.display(description='تاریخ عضویت')
    def get_date_joined_jalali(self, obj):
        return datetime2jalali(obj.date_joined).strftime('%a, %d %b %Y %H:%M:%S')

    @admin.display(description='تاریخ اصلاح')
    def get_date_modified_jalali(self, obj):
        return datetime2jalali(obj.date_modified).strftime('%a, %d %b %Y %H:%M:%S')

    # @admin.display(description='تولد')
    # def get_date_of_birth(self, obj):
    #     return datetime2jalali(obj.date_of_birth).strftime("%Y/%m/%d")


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
            "fields": ("first_name", "last_name", "address", "gender", "date_of_birth", "photo")
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
        ('Customer Fields', {
            'fields': ('address',)
        }),
        ("Permissions", {
            "fields": ("is_superuser", "is_staff", "is_active", "groups", "user_permissions")
        }),
    )

    readonly_fields = ('date_joined', 'date_modified', 'last_login')

    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(Customer, CustomerAdmin)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('zip_code', 'street', 'city', 'state')
    list_filter = ('city',)
