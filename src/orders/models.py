from django.db import models
from customers.models import DateFieldsMixin
from customers.models import Customer
from website.models import Product
from django.core.validators import MinValueValidator



# Create your models here.


class Order(DateFieldsMixin, models.Model):
    class STATE(models.TextChoices):
        UNPAID = 'UNPAID', "ناپرداخت"
        PAID = 'PAID', "پرداخت"
        CANCELLED = 'CANCELLED', "کنسل"
        PROCESSING = 'PROCESSING', "درحال بسته بندی"

    state = models.CharField(max_length=20, choices=STATE.choices, default=STATE.UNPAID)
    total_cost = models.PositiveBigIntegerField(default=0)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class OrderItem(DateFieldsMixin, models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.PositiveIntegerField(default=0)
    discounted_price = models.PositiveIntegerField(default=0, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.price = self.product.price
            self.discounted_price = self.product.discounted_price
        self.total_discounted_price = self.quantity * self.discounted_price
        # TODO: don't let the discounted_price to become greater than 'Price' in updates
        super().save(*args, **kwargs)
        self.order.save()
