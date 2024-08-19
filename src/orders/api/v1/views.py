from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from orders.models import Order, OrderItem
from rest_framework import generics, viewsets
from .serializers import OrderSerializer, OrderItemSerializer


class OrderListAPIView(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    # permission_classes = [
    #     IsStaffAuthenticated
    # ]

    # def get_queryset(self):
    #     user = self.request.user
    #     result = super().get_queryset()
    #     if not user.is_staff:
    #         result = result.filter(customer__username=user.username)
    #     return result


class OrderDetailAPIView(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    lookup_url_kwarg = 'pk'
    # permission_classes = [
    #     IsOwnerUser
    # ]

class OrderItemListAPIView(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    queryset =OrderItem.objects.all()


# class OrderDetailView(APIView):
#
#     def get_object(self, pk):
#         try:
#             return Order.objects.get(pk=pk)
#         except Order.DoesNotExist:
#             raise Http404
#
#     def get(self, request, pk, format=None):
#         order = self.get_object(pk)
#         serializer = OrderSerializer(order)
#         return Response(serializer.data)
#
#     def put(self, request, pk, format=None):
#         order = self.get_object(pk)
#         serializer = OrderSerializer(order, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk, format=None):
#         order = self.get_object(pk)
#         if order:
#             order.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#
# class UpdateOrderView(APIView):
#     def post(self, request, *args, **kwargs):
#         product_id = request.data.get('product_id')
#         product = Product.objects.get(id=product_id)
#         if request.user.is_authenticated:
#             customer = Customer.objects.get(id=request.user.pk)
#             order, created = Order.objects.get_or_create(customer=customer, state=Order.STATE.UNPAID)
#             orderitem, created = OrderItem.objects.get_or_create(order=order, product=product)
#             orderitem.quantity += 1
#             orderitem.save()
#
#             order_serializer = OrderSerializer(order)
#             return Response({
#                 'message': 'اد شد',
#                 'order': order_serializer.data
#             })
#         else:
#             return Response({'error': 'کاربر لاگین نیست'}, status=status.HTTP_403_FORBIDDEN)
