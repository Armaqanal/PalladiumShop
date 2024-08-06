from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.PalladiumLoginView.as_view(), name='login'),
    path('logout/', views.PalladiumLogoutView.as_view(), name='logout'),
]