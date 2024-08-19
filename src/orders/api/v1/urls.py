from django.urls import path
from .views import OrderDetailAPIView, OrderListAPIView

urlpatterns = [
    path('list/', OrderListAPIView.as_view({'get': 'list'}), name='order-list'),
    path('detail/<int:pk>', OrderDetailAPIView.as_view({'get': 'retrieve'}), name='order-detail'),
]
