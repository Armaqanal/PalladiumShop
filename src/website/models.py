import os
from django.db import models
from django.utils import timezone
from customers.models import DateFieldsMixin
from django.core.validators import (MinLengthValidator, MaxLengthValidator,
                                    MinValueValidator, MaxValueValidator)
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from vendors.models import Company
from django.utils.text import slugify
from django.urls import reverse_lazy

from website.manager import ApprovedCommentManager

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام")
    subcategories = models.ForeignKey(
        "self", default=None, null=True, blank=True, on_delete=models.SET_NULL, related_name="parent_categories",
        verbose_name="زیر مجموعه ها"
    )
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, allow_unicode=True)

    def save(self, *args, **kwargs):
        # todo: if the label gets updated the slug wouldn't be matched!
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی‌ها"

    def __str__(self):
        return self.name


class Discount(models.Model):
    percent = models.IntegerField(default=0, null=True, blank=True,
                                  verbose_name="درصد", help_text="چند درصد تخفیف؟")
    amount = models.PositiveBigIntegerField(default=0, verbose_name="چقدر تخفیف؟")
    start_date = models.DateTimeField(default=timezone.now, null=True, blank=True,
                                      verbose_name="زمان شروع")
    end_date = models.DateTimeField(default=None, null=True, blank=True,
                                    verbose_name="زمان پایان")

    def is_active(self) -> bool:
        now = timezone.now()
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True

    def clean(self):
        if self.percent is not None and self.amount > 0:
            raise ValueError("شما نمیتوانید هم درصدی هم مقداری تخفیف بزارید")

    def calculate_price(self, price: int) -> int:
        self.clean()
        if not self.is_active():
            return price

        if self.percent is not None:
            discount_value = (price * self.percent) / 100
            final_price = price - discount_value
        else:
            final_price = price - self.amount

        return max(final_price, 0)


class Product(DateFieldsMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم")
    price = models.PositiveIntegerField(default=0)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, related_name="products", verbose_name="تخفیف",
                                 null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    inventory = models.PositiveIntegerField(default=0, verbose_name="انبار")
    rating_count = models.IntegerField(default=0)
    sum_rating = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=2, decimal_places=1,
                                         default=1.0,
                                         validators=[
                                             MinValueValidator(1.0),
                                             MaxValueValidator(5.0)
                                         ])
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="products",
                                verbose_name="شرکت")
    description = models.CharField(max_length=255, null=True, blank=True)

    slug = models.SlugField(max_length=100, blank=True, null=True, allow_unicode=True)

    def change_inventory(self, change: int):
        new_inventory = self.inventory + change
        if new_inventory >= 0:
            self.inventory = new_inventory
            self.save()
        else:
            raise ValueError("انبار نمیتونه منفی باشه")

    @property
    def final_price(self) -> int:
        result = self.price
        if self.discount is not None and self.discount.is_active():
            result = self.discount.calculate_price(result)
        return result

    final_price.fget.short_description = "قیمت نهایی"

    def update_average_rating(self):
        if self.rating_count > 0:
            self.average_rating = round(self.sum_rating / self.rating_count, 1)

    def get_absolute_url(self):
        return reverse_lazy('website:product-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        return super().save(*args, **kwargs)

    # def get_absolute_url(self):
    #     return reverse('category-detail', kwargs={'slug': self.slug})




class ProductRating(DateFieldsMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} :: {self.product.name} :: {self.rating}"

    def save(self, *args, **kwargs):
        if self.pk:
            old_rating = ProductRating.objects.get(pk=self.pk)
            rating_diff = self.rating - old_rating.rating
            self.product.sum_rating += rating_diff
        else:
            self.product.rating_count += 1
            self.product.sum_rating += self.rating

        self.product.update_average_rating()
        self.product.save()
        super().save(*args, **kwargs)


@receiver(post_delete, sender=ProductRating)
def update_product_rating_on_delete(sender, instance, **kwargs):
    product = instance.product
    product.rating_count -= 1
    product.sum_rating -= instance.rating
    product.update_average_rating()
    product.save()


class Comment(DateFieldsMixin, models.Model):
    class STATE(models.TextChoices):
        REGISTERED = 'registered', "موفق"
        REJECTED = 'rejected', "ناموفق"
        PENDING = 'pending', "در انتظار تأیید"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    state = models.CharField(max_length=20, choices=STATE.choices, default=STATE.PENDING)

    objects = models.Manager()
    approved = ApprovedCommentManager()

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} :: {self.product.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.state = Comment.STATE.PENDING
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    def product_image_upload_to(self, filename):
        return f"product_images/{self.product.category}/{filename}"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_upload_to, null=True,
                              blank=True, verbose_name="عکس محصول")

    def __str__(self):
        return f"{self.product.name} Image"

@receiver(post_delete, sender=ProductImage)
def delete_product_image(sender, instance: ProductImage, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
