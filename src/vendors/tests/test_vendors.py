from django.test import TestCase
from customers.models import Customer
from vendors.models import Company, Vendor
from website.models import Product
from orders.models import Order, OrderItem
import time
from website.models import Category


class CompanyModelTest(TestCase):
    def setUp(self):
        self.company1 = Company.objects.create(name="Company1", address="Address 1")
        time.sleep(0.01)
        self.company2 = Company.objects.create(name="Company2", address="Address 2")
        self.category1 = Category.objects.create(name="Test Category1")
        self.category2 = Category.objects.create(name="Test Category2")
        self.product1 = Product.objects.create(name="Product1", price=100, inventory=10, company=self.company1,
                                               category=self.category1)
        self.product2 = Product.objects.create(name="Product2", price=150, inventory=5, company=self.company2,
                                               category=self.category2)
        self.customer = Customer.objects.create(username='testcustomer', email='testcustomer@example.com')
        self.order1 = Order.objects.create(customer=self.customer, state=Order.STATE.PAID)
        self.order2 = Order.objects.create(customer=self.customer, state=Order.STATE.UNPAID)
        OrderItem.objects.create(order=self.order1, product=self.product1, quantity=2, price=self.product1.price)
        OrderItem.objects.create(order=self.order2, product=self.product2, quantity=3, price=self.product2.price)

    def test_get_newest_companies(self):
        companies = Company.get_newest_companies()
        self.assertEqual(companies[0], self.company2)
        self.assertEqual(companies[1], self.company1)

    def test_slug_generation_on_save(self):
        company = Company.objects.create(name="New Company", address="New Address")
        self.assertEqual(company.slug, "new-company")


class VendorModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company", address="Test Address")
        self.vendor_owner = Vendor.objects.create(username='owner', email='owner@example.com', company=self.company,
                                                  role=Vendor.Roles.OWNER)
        self.vendor_manager = Vendor.objects.create(username='manager', email='manager@example.com',
                                                    company=self.company, role=Vendor.Roles.MANAGER)
        self.vendor_operator = Vendor.objects.create(username='operator', email='operator@example.com',
                                                     company=self.company, role=Vendor.Roles.OPERATOR)

    def test_vendor_is_manager(self):
        self.assertTrue(self.vendor_manager.is_manager)
        self.assertFalse(self.vendor_manager.is_owner)
        self.assertFalse(self.vendor_manager.is_operator)

    def test_vendor_save_sets_is_staff(self):
        vendor = Vendor.objects.create(username='staff', email='staff@example.com', company=self.company,
                                       role=Vendor.Roles.OPERATOR)
        self.assertTrue(vendor.is_staff)
