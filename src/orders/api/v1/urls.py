from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrderDetailAPIView, OrderListAPIView, OrderItemListAPIView, OrderItemDetailAPIView, \
    OrderCustomerListAPIView, OrderItemCustomerDetailApiView

router = DefaultRouter()
router.register(r'orders', OrderListAPIView, basename='orders')
urlpatterns = [
    path('', include(router.urls)),
    path('detail/order/item/<int:pk>/', OrderItemDetailAPIView.as_view({'get': 'retrieve'}),
         name='order-item-detail-vendor'),
    path('orders/<int:pk>/items/', OrderItemListAPIView.as_view({'get': 'list'}), name='order-item-list'),


    path('detail/<int:pk>/order', OrderDetailAPIView.as_view({'get': 'retrieve',
                                                              'put': 'update',
                                                              'patch': 'partial_update',
                                                              'delete': 'destroy', }), name='order-detail'),

    # path('list/order-item', OrderItemListAPIView.as_view({'get': 'list'}), name='order-item-list'),
    path('list/order/customer', OrderCustomerListAPIView.as_view({'get': 'list'}), name='order-list-customer'),
    path('api/v1/list/order/item/customer/<int:pk>/', OrderItemCustomerDetailApiView.as_view({'get': 'list'}),
         name='order-item-detail-customer'),  # TODO NOT PK SHOULD BE ORDER_ID
]
