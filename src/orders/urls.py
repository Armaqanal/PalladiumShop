from django.urls import path
from .views import AddToCartView, CheckoutView, UpdateQuantityView, CartQuantityView, DeleteOrderItemView

app_name = 'orders'

urlpatterns = [
    path('add/', AddToCartView.as_view(), name='add'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('cart_quantity/', CartQuantityView.as_view(), name='cart_quantity'),
    path('update-quantity/', UpdateQuantityView.as_view(), name='update-quantity'),
    path('delete-order-item/', DeleteOrderItemView.as_view(), name='delete_order_item'),

    # path('orders/history/', OrderHistoryListView.as_view(), name='order_history'),
]
