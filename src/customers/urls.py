from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'customers'

urlpatterns = [
    path('profile/', views.CustomerProfileView.as_view(), name='profile'),
    path('edit-profile/', views.CustomerEditProfileView.as_view(), name='profile-edit'),
    path('detele-photo/', views.CustomerDeletePhoto.as_view(), name='profile-delete'),

    path('address/', views.CustomerAddress.as_view(), name='customer-address'),
    path('address/<int:pk>/delete', views.CustomerDeleteAddressView.as_view(), name='delete_address'),
    path('address/<int:pk>/update', views.CustomerUpdateView.as_view(), name='update-address'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
