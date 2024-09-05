from orders.models import Order, OrderItem
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import OrderSerializer, OrderItemSerializer, OrderSerializerCustomer
from .permissions import IsStaffUser, IsCustomerUser
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger('orders')

logger.debug('Debug message for testing')
logger.info('Info message for testing')
logger.error('Error message for testing')


class OrderListAPIView(viewsets.GenericViewSet,
                       viewsets.mixins.ListModelMixin):
    '''
    Staff user can view all orders --> List all orders
    Staff can change state of orders --> Change state
    '''
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]

    def get_queryset(self):
        user = self.request.user.vendor
        vendor_company = user.company
        if vendor_company:
            queryset = Order.objects.filter(order_items__product__company=vendor_company).distinct()
            return queryset
        return Order.objects.none()

    def get_serializer_context(self):
        return {'request': self.request}

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        state = request.data.get('state', None)

        if state is not None:
            order.state = state
            order.save()
            serializer = self.get_serializer(order)
            return Response(serializer.data)

        return Response({'message': 'State is not valid'}, status=status.HTTP_400_BAD_REQUEST)


class OrderItemDetailAPIView(viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return OrderItem.objects.all()


class OrderItemListAPIView(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]

    def get_queryset(self):
        user = self.request.user.vendor
        company_id = user.company.id
        order_id = self.kwargs.get('pk')
        if order_id:
            return OrderItem.objects.filter(order_id=order_id, product__company_id=company_id)
        return OrderItem.objects.none()


class OrderDetailAPIView(viewsets.ModelViewSet):
    '''
    staff user can delete,put,patch all orders -->for post need order_items
    '''
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
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
