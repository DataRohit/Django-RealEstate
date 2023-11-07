import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import IntegrityError
from django.db import models


__all__ = ["User"]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError("Email is a required field.")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        unique=True,
        verbose_name="Email Address",
        error_messages={"unique": ("A user with this email already exists.")},
    )
    first_name = models.CharField(max_length=30, verbose_name="First Name")
    last_name = models.CharField(max_length=30, verbose_name="Last Name")
    phone = models.CharField(
        max_length=10,
        verbose_name="Phone Number",
        blank=True,
        validators=[
            RegexValidator(
                regex="^[0-9-()+]{10,20}$",
                message=("Please enter a valid phone number."),
                code="phone_format",
            )
        ],
    )
    is_staff = models.BooleanField(
        default=False,
        help_text=("Designates whether the user can log into this admin site."),
        verbose_name="Staff Status",
    )
    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
        verbose_name="Active",
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    _ALL_TYPES_ALLOWED = set(["Homebuyer", "Realtor"])
    _HOMEBUYER_ONLY = set(["Homebuyer"])
    _REALTOR_ONLY = set(["Realtor"])

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    def clean(self):
        if hasattr(self, "homebuyer") and hasattr(self, "realtor"):
            raise ValidationError("User cannot be a Homebuyer and a Realtor.")
        return super(User, self).clean()

    def clean_fields(self, exclude=None):
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        return super(User, self).clean_fields(exclude=exclude)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    @property
    def role_object(self):
        has_homebuyer = hasattr(self, "homebuyer")
        has_realtor = hasattr(self, "realtor")

        if has_homebuyer:
            if has_realtor:
                raise IntegrityError(
                    f"User {str(self)} is registered as both a Homebuyer and a Realtor, which is not valid."
                )
            return self.homebuyer
        elif has_realtor:
            return self.realtor
        return None
