from orders.models import Order, OrderItem
from rest_framework import viewsets
from .serializers import OrderSerializer, OrderItemSerializer, OrderSerializerCustomer
from .permissions import IsStaffUser, IsCustomerUser
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


class OrderCustomerListAPIView(viewsets.ModelViewSet):
    serializer_class = OrderSerializerCustomer
    permission_classes = [IsCustomerUser]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)


class OrderItemCustomerDetailApiView(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializerCustomer
    permission_classes = [IsCustomerUser]

    def get_queryset(self):
        order_id = self.kwargs.get('pk')
        return OrderItem.objects.filter(order_id=order_id, order__customer=self.request.user)
