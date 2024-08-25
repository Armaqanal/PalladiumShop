from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('profile/', views.VendorProfileView.as_view(), name='profile'),
    path('edit-profile/', views.VendorEditProfileView.as_view(), name='profile-edit'),
    # path('detele-photo/', views.CustomerDeletePhoto.as_view(), name='profile-delete'),
    # 
    # path('address/', views.CustomerAddress.as_view(), name='customer-address'),
    # path('address/<int:pk>/delete', views.CustomerDeleteAddressView.as_view(), name='delete_address'),
    # path('address/<int:pk>/update', views.CustomerUpdateView.as_view(), name='update-address'),

    path('best/companies/', views.BestCompany.as_view(), name='best-companies'),
]

