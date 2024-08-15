import logging
from datetime import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator

from customers.managers import UserManager
import os
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver


class DateFieldsMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ ویرایش")

    class Meta:
        abstract = True


class User(AbstractUser):
    # def profile_image_upload_to(instance, filename):
    #     extension = Path(filename).suffix
    #     return f"profile_photos/{instance.__class__.__name__.lower()}/{instance.username}{extension}"

    class Gender(models.TextChoices):
        MALE = "M", "مرد"
        FEMALE = "F", "زن"

    # Validators
    username_validator = UnicodeUsernameValidator()
    phone_regex = RegexValidator(
        regex="^(\\+98|0)?9\\d{9}$", message="شماره تلفن معتبر نمی‌باشد!"
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=(
            "اجباری. حداکثر ۱۵۰ کاراکتر. حروف، ارقام و @/./+/-/_ فقط."
        ),
        validators=[username_validator],
        error_messages={
            "unique": "کاربری با این نام کاربری وجود دارد.",
        },
        null=True,
        blank=True,
        verbose_name="نام کاربری"
    )
    phone = models.CharField(
        max_length=40,
        unique=True,
        validators=[phone_regex],
        null=True,
        blank=True,
        default=None,
        verbose_name="شماره تلفن"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="ایمیل",
        null=True, blank=True, default=None
    )

    # photo = models.ImageField(upload_to=profile_image_upload_to, null=True, blank=True, verbose_name="عکس")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="تاریخ تولد")
    gender = models.CharField(max_length=1, choices=Gender.choices, verbose_name="جنسیت")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ عضویت")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="تاریخ اصلاح")
    photo = models.ImageField(upload_to='profile_photos', null=True, blank=True, verbose_name="عکس")

    objects = UserManager()

    REQUIRED_FIELDS = ["email", "phone"]

    @property
    def age(self):
        today = timezone.now().date()
        age = int(
            today.year
            - self.date_of_birth.year
            - (
                    (today.month, today.day)
                    < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )
        return age

    def __str__(self):
        return self.username or self.email or self.phone

    def save(self, *args, **kwargs):

        if not (self.username or self.email or self.phone):
            raise ValueError("Providing username, email or phone number is required.")

        if self.email == "":
            self.email = None
        if self.username == "":
            self.username = None
        if self.phone == "":
            self.phone = None

        super().save(*args, **kwargs)

    @property
    def is_customer(self):
        return not self.is_staff


class Admin(User):
    class Meta:
        proxy = True
        verbose_name = "ادمین"
        verbose_name_plural = 'ادمین ها'

    def save(self, *args, **kwargs):
        self.is_superuser = True
        self.is_staff = True
        super().save(*args, **kwargs)


class Customer(User):
    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتری‌ها"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Address(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='addresses')

    street = models.CharField(max_length=10, verbose_name="خیابان")
    city = models.CharField(max_length=100, verbose_name="شهر")
    state = models.CharField(max_length=50, verbose_name="ایالت")
    zip_code = models.CharField(
        max_length=10,
        blank=True,
        validators=[MinLengthValidator(10), MaxLengthValidator(10)], verbose_name="کد پستی")

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"

    def __str__(self):
        return f"{self.state}, {self.city}, {self.street}"


@receiver(post_delete, sender=User)
def delete_customer_profile_photo(sender, instance: User, **kwargs):
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)

# logger = logging.getLogger(__name__)


# @receiver(post_save, sender=User)
# def handle_photo_upload(sender, instance, **kwargs):
#     # Check if the photo was updated or newly uploaded
#     if instance.photo and kwargs.get('created', False):
#         logger.info(f"New photo uploaded: {instance.photo.url}")
#     elif instance.photo:
#         logger.info(f"Photo updated: {instance.photo.url}")
