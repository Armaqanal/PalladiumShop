from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.PalladiumLoginView.as_view(), name='login'),
    path('logout/', views.PalladiumLogoutView.as_view(), name='logout'),
    path('register/', views.PalladiumRegisterView.as_view(), name='register'),

    path('register/vendor/', views.PalladiumOwnerRegisterView.as_view(), name='register-vendor'),
]
