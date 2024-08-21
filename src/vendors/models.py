from django.db import models
from customers.models import DateFieldsMixin, User
from django.core.validators import (MinLengthValidator, MaxLengthValidator,
                                    MinValueValidator, MaxValueValidator)

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify


class Company(DateFieldsMixin, models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="شرکت")
    address = models.CharField(max_length=200, verbose_name="آدرس")
    # vendors = models.ForeignKey('Vendor', on_delete=models.CASCADE, verbose_name="فروشندگان", related_name="companies")
    slug = models.SlugField(max_length=100, blank=True, null=True, allow_unicode=True)
    rating_count = models.IntegerField(default=0)
    sum_rating = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=2, decimal_places=1,
                                         default=1.0,
                                         validators=[
                                             MinValueValidator(1.0),
                                             MaxValueValidator(5.0)
                                         ])

    def update_average_rating(self):
        if self.rating_count > 0:
            self.average_rating = round(self.sum_rating / self.rating_count, 1)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class CompanyRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('company', 'user')

    def __str__(self):
        return f"{self.user.username} :: {self.company.name} :: {self.rating}"

    def save(self, *args, **kwargs):
        if self.pk:
            old_rating = CompanyRating.objects.get(pk=self.pk)
            rating_diff = self.rating - old_rating.rating
            self.company.sum_rating += rating_diff
        else:
            self.company.rating_count += 1
            self.company.sum_rating += self.rating

        self.company.update_average_rating()
        self.company.save()
        super().save(*args, **kwargs)


@receiver(post_delete, sender=CompanyRating)
def update_company_rating_on_delete(sender, instance, **kwargs):
    company = instance.company
    company.rating_count -= 1
    company.sum_rating -= instance.rating
    company.update_average_rating()
    company.save()


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
