import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Customer, Address
from django.utils import timezone
from datetime import date


class TestCustomer(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(username='test', password='armaqan123', email='testcase1@gmail.com',
                                                phone='09129879877', date_of_birth=date(1990, 1, 1), gender='M')
        self.customer.set_password('armaqan123')
        self.customer.save()

        self.address = Address.objects.create(customer=self.customer, street='test street', city='test', state='test',
                                              zip_code='9876543245')

        # self.photo = SimpleUploadedFile(name='test_photo.jpg', content=b'', content_type='image/jpeg')
        # self.customer.photo = self.photo
        self.customer.save()

        self.client = Client()
        self.client.login(username='test', password='armaqan123')

        self.delete_photo_url = reverse('customers:profile-delete')

    '''
         Testcase for model ---> age
    '''

    def test_age_calculation(self):
        today = timezone.now().date()
        expected_age = today.year - 1990 - ((today.month, today.day) < (1, 1))
        self.assertEqual(self.customer.age, expected_age)

    '''
        Testcase for CustomerView
    '''

    def test_customer_view(self):
        response = self.client.get(reverse('customers:profile'))
        self.assertEqual(response.status_code, 200)

    # def test_delete_photo_view(self):
    #     response = self.client.post(self.delete_photo_url)
    #     self.customer.refresh_from_db()
    #     self.assertIsNone(self.customer.photo)  # failure
    #     self.assertFalse(os.path.isfile(self.photo.path))
    #     self.assertRedirects(response, reverse('customers:profile-edit'))
    # TODO aksa az media pak nemishan + database
