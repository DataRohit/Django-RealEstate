# UUID import for primary key
import uuid


# Django imports
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import IntegrityError
from django.db import models


# List of models to export
__all__ = ["User"]


# Class for User Manager
class UserManager(BaseUserManager):
    # Set flag for migrations
    use_in_migrations = True

    # Function to create user
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        # If the email is not provided
        if not email:
            # Raise a value error
            raise ValueError("Email is a required field.")

        # Get the normalized email
        email = self.normalize_email(email)

        # Create a new user instance
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            **extra_fields,
        )

        # Set the password for the user instance
        user.set_password(password)

        # Save the user instance to the database
        user.save(using=self._db)

        # Return the created user
        return user

    # Function to create a normal user
    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    # Function to create a super user
    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


# Class for custom user model
class User(AbstractUser, PermissionsMixin):
    # Custom uuid field for primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Fields for the user model
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

    # Initialize the user manager object
    objects = UserManager()

    # Set the fields for the user model
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # Set protected variables for the user model
    _ALL_TYPES_ALLOWED = set(["Homebuyer", "Realtor"])
    _HOMEBUYER_ONLY = set(["Homebuyer"])
    _REALTOR_ONLY = set(["Realtor"])

    # Meta class for user model
    class Meta:
        # Set the verbose name and plural name for the user model
        verbose_name = "User"
        verbose_name_plural = "Users"

    # String representation
    def __str__(self):
        return self.email

    # Method to clean the user model
    def clean(self):
        # If the user is a homebuyer and a realtor
        if hasattr(self, "homebuyer") and hasattr(self, "realtor"):
            # Raise a validation error
            raise ValidationError("User cannot be a Homebuyer and a Realtor.")

        # Call the clean method of the parent class
        return super(User, self).clean()

    # Method to clean the fields of the user model
    def clean_fields(self, exclude=None):
        # Get the cleaned fields
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()

        # Call the clean fields method of the parent class
        return super(User, self).clean_fields(exclude=exclude)

    # Method to send an email to the user
    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    # Method to get the full name of the user
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    # Method to get the short name of the user
    def get_short_name(self):
        return self.first_name

    # Property to get the role of the user
    @property
    def role_object(self):
        # Get the role of the user
        has_homebuyer = hasattr(self, "homebuyer")
        has_realtor = hasattr(self, "realtor")

        # If the user is a homebuyer
        if has_homebuyer:
            # And the user is a realtor
            if has_realtor:
                # Raise an integrity error
                raise IntegrityError(
                    f"User {str(self)} is registered as both a Homebuyer and a Realtor, which is not valid."
                )

            # Return the homebuyer status
            return self.homebuyer

        # If the user is a realtor
        elif has_realtor:
            # Return the realtor status
            return self.realtor

        # Else return None
        return None
