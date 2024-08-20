from orders.models import Order, OrderItem
from rest_framework import generics, viewsets
from .serializers import OrderSerializer, OrderItemSerializer
from .permissions import IsStaffUser
from rest_framework.permissions import IsAuthenticated


class OrderListAPIView(viewsets.ModelViewSet):
    '''
    staff user can view all orders -->List all orders
    '''
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated, IsStaffUser]


class OrderDetailAPIView(viewsets.ModelViewSet):
    '''
    staff user can delete,put,patch all orders -->for post need order_items
    '''
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    lookup_url_kwarg = 'pk'
    permission_classes = [IsAuthenticated, IsStaffUser]


class OrderItemListAPIView(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()
    permission_classes = [IsAuthenticated, IsStaffUser]



class OrderItemDetailAPIView(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()
    lookup_url_kwarg = 'pk'
    permission_classes = [IsAuthenticated, IsStaffUser]
