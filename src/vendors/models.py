from django.utils import timezone
from django.db import models
from customers.models import DateFieldsMixin, Customer, User

from django.db.models import Q, Sum, Count, F, DecimalField, ExpressionWrapper

from django.utils.text import slugify


# from orders.models import Order


class Company(DateFieldsMixin, models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="شرکت")
    address = models.CharField(max_length=200, verbose_name="آدرس")
    slug = models.SlugField(max_length=100, blank=True, null=True, allow_unicode=True)
    logo = models.ImageField(upload_to='companies_logo', null=True, blank=True, verbose_name="عکس")

    @classmethod
    def get_best_company(cls, limit=None):
        from django.apps import apps
        Order = apps.get_model('orders', 'Order')

        companies = cls.objects.annotate(
            total_sales=Sum(
                'products__order_items__subtotal',
                filter=Q(products__order_items__order__state=Order.STATE.PAID)
            )
        ).order_by('-total_sales')

        if limit:
            companies = companies[:limit]
        return companies

    @classmethod
    def get_best_company_rate(cls, limit=None):
        companies = cls.objects.annotate(
            total_products_rate=Sum('products__average_rating'),
            total_products=Count('products')
        ).annotate(
            average_company_rate=ExpressionWrapper(
                F('total_products_rate') / F('total_products'),
                output_field=DecimalField()
            )
        ).order_by('-average_company_rate')

        if limit:
            companies = companies[:limit]

        return companies

    @classmethod
    def get_newest_companies(cls, limit=None):
        companies = cls.objects.filter(created_at__lte=timezone.now()).order_by('-created_at')
        if limit:
            companies = companies[:limit]
        return companies

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Vendor(User):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='vendors')

    class Roles(models.TextChoices):
        OWNER = "OWNER", "مدیر فروشگاه"
        MANAGER = "MANAGER", "مدیر محصول"
        OPERATOR = "OPERATOR", "ناظر"

    role = models.CharField(
        max_length=25, choices=Roles.choices, default=Roles.OWNER, verbose_name="نقش ها"
    )

    @property
    def is_manager(self):
        return self.role == self.Roles.MANAGER

    @property
    def is_owner(self):
        return self.role == self.Roles.OWNER

    @property
    def is_operator(self):
        return self.role == self.Roles.OPERATOR

    class Meta:
        verbose_name = "فروشنده"
        verbose_name_plural = "فروشندگان"

    def save(self, *args, **kwargs):
        self.is_staff = True
        super().save(*args, **kwargs)
