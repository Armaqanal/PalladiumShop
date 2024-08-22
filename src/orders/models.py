from django.db import models
from customers.models import DateFieldsMixin
from customers.models import Customer, Address
from website.models import Product
from django.core.validators import MinValueValidator
from django.db.models.functions import Coalesce
from django.db.models import Sum, IntegerField, Value


class Order(DateFieldsMixin, models.Model):
    class STATE(models.TextChoices):
        UNPAID = 'UNPAID', "ناپرداخت"
        PAID = 'PAID', "پرداخت"

    state = models.CharField(max_length=20, choices=STATE.choices, default=STATE.UNPAID)
    total_cost = models.PositiveBigIntegerField(default=0)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)

    # TODO beacuse customer dont add address in the registration form

    def grand_total(self):
        self.total_cost = self.order_items.aggregate(
            sum=Coalesce(
                Sum('subtotal'), Value(0)
            )
        )['sum']

    @property
    def order_quantity(self):
        return self.order_items.aggregate(total_quantity=Coalesce(Sum('quantity'), Value(0)))['total_quantity']

    def save(self, *args, **kwargs):
        if self.pk:
            self.grand_total()
            quantity = self.order_quantity
        super().save(*args, **kwargs)


class OrderItem(DateFieldsMixin, models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.PositiveIntegerField(default=0)
    discounted_price = models.PositiveIntegerField(default=0, blank=True)
    subtotal = models.PositiveBigIntegerField(default=0, blank=True)

    @property
    def calculated_subtotal(self):
        return self.quantity * self.discounted_price

    def save(self, *args, **kwargs):
        if not self.pk:
            self.price = self.product.price
        self.discounted_price = self.product.final_price

        if self.discounted_price > self.price:
            raise ValueError("Discounted price cannot be greater than the original price")

        self.subtotal = self.calculated_subtotal
        super().save(*args, **kwargs)
        self.order.save()

    def update_quantity(self, new_quantity: int):
        if new_quantity <= 0:
            raise ValueError('تعداد باید مثبت باشد')

        quantity_change = new_quantity - self.quantity
        if quantity_change > 0:
            if self.product.inventory < quantity_change:
                raise ValueError('انبار کافی نیست')
        elif quantity_change < 0:
            self.product.change_inventory(-quantity_change)

        self.quantity = new_quantity
        self.subtotal = self.calculate_subtotal
        self.save()

        if quantity_change > 0:
            self.product.change_inventory(-quantity_change)
