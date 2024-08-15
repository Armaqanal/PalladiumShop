from django.contrib import admin
from customers.admin import PalladiumUserAdmin
# from .forms import UserChangeForm, UserCreationForm
from .models import Vendor, Company



# class VendorAdmin(PalladiumUserAdmin):
#     add_form = UserCreationForm
#     form = UserChangeForm
#     model = Vendor
#
#     fieldsets = (
#         (None, {
#             "fields": ("username", "email", "phone", "password")
#         }),
#         ('Personal Info', {
#             "fields": ("first_name", "last_name", "gender", "date_of_birth", "photo")
#         }),
#         ("Permissions", {
#             "fields": ("is_superuser", "is_staff", "is_active", "groups", "user_permissions")
#         }),
#     )
#
#     add_fieldsets = (
#         (None, {
#             "classes": ("wide",),
#             "fields": ("username", "email", "phone", "password1", "password2")
#         }),
#         ('Personal Info', {
#             "fields": ("first_name", "last_name", "gender", "date_of_birth", "photo")
#         }),
#         ("Permissions", {
#             "fields": ("is_superuser", "is_staff", "is_active", "groups", "user_permissions")
#         }),
#     )
#
#     readonly_fields = ('date_joined', 'date_modified', 'last_login')
#
#     search_fields = ("email",)
#     ordering = ("email",)


# admin.site.register(Vendor, VendorAdmin)
admin.site.register(Vendor)
admin.site.register(Company)