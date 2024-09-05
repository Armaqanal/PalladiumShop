from rest_framework import serializers
from orders.models import Order, OrderItem
from website.models import Product
from customers.models import Customer, Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone', 'email']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'final_price']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    order_items = serializers.HyperlinkedRelatedField(read_only=True, many=True, view_name='order-item-detail-vendor')
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'state', 'total_cost', 'order_items', 'order_quantity', 'customer', 'address']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context['request'].method == 'PATCH':
            return {'state': representation['state']}
        return representation


class OrderSerializerCustomer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    order_items = serializers.HyperlinkedRelatedField(read_only=True, many=True, view_name='order-item-detail-customer')

    class Meta:
        model = Order
        fields = ['id', 'total_cost', 'customer', 'state', 'order_items']


class OrderItemSerializerCustomer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'price', 'name']
