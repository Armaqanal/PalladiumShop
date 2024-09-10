from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('profile/', views.VendorProfileView.as_view(), name='profile'),
    path('edit-profile/', views.VendorEditProfileView.as_view(), name='profile-edit'),

    path('companies/', views.CompaniesView.as_view(), name='companies'),
    path('company/list/', views.CompanyListView.as_view(), name='company-list'),

    path('vendor/list/<int:company_id>/', views.VendorsListView.as_view(), name='vendor-list'),
    path('vendor/delete/<int:pk>/', views.VendorDeleteView.as_view(), name='vendor-delete'),

]
