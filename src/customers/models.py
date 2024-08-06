from datetime import timezone

from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator

from pathlib import Path

from customers.managers import UserManager
from django.contrib.auth.hashers import make_password


class DateFieldsMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    def profile_image_upload_to(instance, filename):
        extension = Path(filename).suffix
        return f"profile_photos/{instance.__class__.__name__.lower()}/{instance.username}{extension}"

    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    # Validators
    username_validator = UnicodeUsernameValidator()
    phone_regex = RegexValidator(
        regex="^(\\+98|0)?9\\d{9}$", message="Invalid phone number!"
    )  # TODO: proper message

    username = models.CharField(
        "username",
        max_length=150,
        unique=True,
        help_text=(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
        null=True,
        blank=True,
    )
    phone = models.CharField(
        "phone number",
        max_length=40,
        unique=True,
        validators=[phone_regex],
        null=True,
        blank=True,
        default=None,
    )
    email = models.EmailField(
        "Email Address", unique=True
    )

    photo = models.ImageField(upload_to=profile_image_upload_to, null=True, blank=True)
    date_of_birth = models.DateTimeField("Date Of Birth", null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    objects = UserManager()

    REQUIRED_FIELDS = ["email"]

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
        if not self.email:
            raise ValueError("Email is required")
        # if not (self.username or self.email or self.phone):
        #     raise ValueError("Providing username, email or phone number is required.")

        # if self.email == "":
        #     self.email = None
        if self.username == "":
            self.username = None
        if self.phone == "":
            self.phone = None

        super().save(*args, **kwargs)

    @property
    def is_customer(self):
        return not self.is_staff


class Customer(User):
    address = models.ForeignKey(
        "Address", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتری ها"

    def save(self, *args, **kwargs):
    #     if self.pk is None and self.password:
    #         self.password = make_password(self.password)
    #     elif not self.password.startswith('pbkdf2_'):
    #         self.password = make_password(self.password)
        super().save(*args, **kwargs)


class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(
        max_length=10,
        blank=True,
        validators=[MinLengthValidator(10), MaxLengthValidator(10)]
    )

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس ها"

    def __str__(self):
        return f"{self.state}, {self.city}, {self.street}"
