from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from customers.models import Customer
from vendors.models import Vendor


class TestAccounts(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.customer = Customer.objects.create(username='test', password='armaqan123', email='testcase1@gmail.com',
                                                phone='09129879877', date_of_birth=date(1990, 1, 1), gender='M')
        self.customer.set_password('armaqan123')
        self.customer.save()

    def test_register_success(self):
        '''
        Customer Registration Successfully
        '''
        form_data = {'username': 'test', 'email': 'test@gmail.com', 'password1': 'armaqan123',
                     'password2': 'armaqan123', 'gender': 'M', 'date_of_birth': '1995-01-01', 'phone': '09129879877'}
        response = self.client.post(self.register_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Customer.objects.filter(username='test').exists())

    def test_register_success_vendor(self):
        '''
        Vendor Registration Successfully
        '''
        self.register_url = reverse('accounts:register-vendor')
        form_data = {'username': 'testowner', 'email': 'testowner@gmail.com', 'phone': '09129879878',
                     'password1': 'armaqan123', 'password2': 'armaqan123', 'first_name': 'Test',
                     'last_name': 'Owner',
                     'gender': 'M',
                     'date_of_birth': '1985-01-01',
                     'company_name': 'Test Company',
                     'company_address': '123 Test Address',
                     'photo': '',
                     }
        response = self.client.post(self.register_url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.login_url)
        self.assertTrue(Vendor.objects.filter(username='testowner').exists())

    def test_login_vendor_customer(self):
        '''
        Login for Vendor and Customer is Same
        '''

        user = Customer.objects.get(email='testcase1@gmail.com')
        self.assertTrue(user.check_password('armaqan123'))

        response = self.client.post(self.login_url, {'identifier': 'testcase1@gmail.com', 'password': 'armaqan123'},
                                    follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
