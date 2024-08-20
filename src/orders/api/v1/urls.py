from django.urls import path
from .views import OrderDetailAPIView, OrderListAPIView, OrderItemListAPIView,OrderItemDetailAPIView

urlpatterns = [
    path('list/order', OrderListAPIView.as_view({'get': 'list'}), name='order-list'),
    path('detail/<int:pk>/order', OrderDetailAPIView.as_view({'get': 'retrieve',
                                                              'put': 'update',
                                                              'patch': 'partial_update',
                                                              'delete': 'destroy', }), name='order-detail'),

    path('list/order-item', OrderItemListAPIView.as_view({'get': 'list'}), name='order-item-list'),
    path('detail/<int:pk>/order-item', OrderItemDetailAPIView.as_view({'get': 'retrieve',
                                                              'post': 'create',
                                                              'put': 'update',
                                                              'patch': 'partial_update',
                                                              'delete': 'destroy', }), name='order-item-detail'),
]
