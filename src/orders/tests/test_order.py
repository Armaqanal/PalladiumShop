from datetime import date
from django.test import TestCase
from customers.models import Customer, Address
from vendors.models import Company
from website.models import Category
from orders.models import Order, OrderItem
from website.models import Product


class TestOrder(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(username='test', password='armaqan123', email='testcase1@gmail.com',
                                                phone='09129879877', date_of_birth=date(1990, 1, 1), gender='M')
        self.address = Address.objects.create(street='Test', city='Test', state='test', zip_code='1234567896',
                                              customer=self.customer)
        self.company = Company.objects.create(name='test company')
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(name='test product', price=90, category=self.category, inventory=10,
                                              company=self.company)

        self.order = Order.objects.create(customer=self.customer, address=self.address)

    def test_save_method_update_grand_total(self):
        item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2, price=self.product.price,
                                        discounted_price=self.product.final_price)
        self.order.save()
        self.assertEqual(self.order.total_cost, 180)
        item.update_quantity(3)
        self.order.save()
        self.assertEqual(self.order.total_cost, 270)


class OrderItemModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.address = Address.objects.create(street='123 Test St', city='Testville', state='TS', zip_code='12345',
                                              customer=self.customer)
        self.company = Company.objects.create(name="Test Company")
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(name="Test Product", price=90, category=self.category, inventory=10,
                                              rating_count=5,
                                              sum_rating=20,
                                              company=self.company
                                              )
        self.order = Order.objects.create(customer=self.customer, address=self.address)
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=1,
                                                   price=self.product.price, discounted_price=self.product.final_price)

    def test_calculated_subtotal(self):
        self.assertEqual(self.order_item.calculated_subtotal, 90)

    def test_save_method(self):
        self.order_item.save()
        self.assertEqual(self.order_item.subtotal, 90)

    def test_update_quantity_not_enough_inventory(self):
        with self.assertRaises(ValueError) as context:
            self.order_item.update_quantity(15)
        self.assertEqual(str(context.exception), 'انبار کافی نیست')
        self.assertEqual(self.order_item.quantity, 1)
