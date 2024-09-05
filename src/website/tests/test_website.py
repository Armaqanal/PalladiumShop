from website.models import Category
from django.test import TestCase
from website.models import Discount, Product, ProductRating, Comment
from django.utils import timezone
from datetime import timedelta, date
from vendors.models import Company
from customers.models import Customer


class CategoryTestCase(TestCase):
    def setUp(self):
        self.parent_category = Category.objects.create(name="Parent Category")
        self.subcategory = Category.objects.create(name="Subcategory", subcategories=self.parent_category)

    def test_is_subcategory(self):
        self.assertFalse(self.parent_category.is_subcategory())
        self.assertTrue(self.subcategory.is_subcategory())


class DiscountModelTest(TestCase):
    def setUp(self):
        self.discount_percent = Discount.objects.create(percent=10, amount=0, start_date=timezone.now())
        self.discount_amount = Discount.objects.create(amount=100, start_date=timezone.now())

    def test_clean(self):
        discount = Discount(percent=10, amount=10, start_date=timezone.now(),
                            end_date=timezone.now() + timedelta(weeks=1))
        with self.assertRaises(ValueError) as context:
            discount.full_clean()
        self.assertEqual(str(context.exception), "شما نمیتوانید هم درصدی هم مقداری تخفیف بزارید")


class ProductModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Company")
        self.category = Category.objects.create(name="Category")
        self.discount = Discount.objects.create(amount=10)  # TODO for percentage Ill get error
        self.product = Product.objects.create(name="Product", price=1000, discount=self.discount,
                                              category=self.category, company=self.company, inventory=10)

    def test_product_creation(self):
        self.assertEqual(self.product.final_price, 990)

    def test_change_inventory(self):
        self.product.change_inventory(-5)
        self.assertEqual(self.product.inventory, 5)

        with self.assertRaises(ValueError):
            self.product.change_inventory(-10)

    def test_update_average_rating(self):
        self.product.rating_count = 3
        self.product.sum_rating = 12
        self.product.update_average_rating()
        self.assertEqual(self.product.average_rating, 4.0)


class ProductRatingModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(name="Test Product", price=1000, category=self.category,
                                              company=self.company)
        self.customer = Customer.objects.create(username='test', password='armaqan123', email='testcase1@gmail.com',
                                                phone='09129879877', date_of_birth=date(1990, 1, 1), gender='M')
        self.rating = ProductRating.objects.create(user=self.customer, product=self.product, rating=4)

    def test_rating_update(self):
        self.rating.rating = 5
        self.rating.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.sum_rating, 5)

    def test_rating_deletion(self):
        self.rating.delete()
        self.product.refresh_from_db()
        self.assertEqual(self.product.rating_count, 0)
        self.assertEqual(self.product.sum_rating, 0)


class CommentModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="company")
        self.category = Category.objects.create(name="category")
        self.product = Product.objects.create(name="Product", price=1000, category=self.category,
                                              company=self.company)
        self.customer = Customer.objects.create(username='test', password='armaqan123', email='testcase1@gmail.com',
                                                phone='09129879877', date_of_birth=date(1990, 1, 1), gender='M')
        self.comment = Comment.objects.create(user=self.customer, product=self.product, text="Comment")

    def test_comment_creation(self):
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.comment.state, Comment.STATE.PENDING)

    def test_comment_state_update(self):
        self.comment.state = Comment.STATE.REGISTERED
        self.comment.save()
        self.assertEqual(self.comment.state, Comment.STATE.REGISTERED)
