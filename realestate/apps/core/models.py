# UUID for the primary key
import uuid


# Django imports
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import models
from django.urls import reverse


# Set the models that are available for import
__all__ = [
    "BaseModel",
    "Person",
    "Homebuyer",
    "Realtor",
    "Couple",
]


# Class for the validation of the categories and couples
class ValidateCategoryCoupleMixin(object):
    # Protedted method for the validation of the categories and couples
    def _validate_categories_and_couples(self):
        # if the primary key is not set, return
        if not self.pk:
            return

        # Get the category couple ids
        category_couple_ids = set(self.categories.values_list("couple", flat=True))

        # If the category couple ids are set
        if category_couple_ids:
            # If the couple id is not in the category couple ids
            if (
                len(category_couple_ids) > 1
                or self.couple_id not in category_couple_ids
            ):
                # Raise a validation error
                raise ValidationError("Invalid categories for this couple.")

        # Return
        return


# Base model for all the models
class BaseModel(models.Model):
    # Custom uuid field for the primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Method to validate the min length
    def _validate_min_length(self, fieldname, min_length):
        # Get the fieldname
        field = getattr(self, fieldname, "")

        # Check for the field and the length
        if not field or len(field) < min_length:
            # If the field is not valid, raise a validation error
            raise ValidationError(
                {fieldname: [f"{fieldname} must be at least length {min_length}"]}
            )

        # Return
        return

    # Method to get the clean fields
    def clean_fields(self, exclude=None):
        # Traverse through the fields
        for field in self._meta.fields:
            # If the field is a char field or a text field
            if isinstance(field, (models.CharField, models.TextField)):
                # Get the fieldname and the value
                fieldname = field.name
                value = getattr(self, fieldname)

                # If the value exist
                if value:
                    # Set the value to the stripped value
                    setattr(self, fieldname, value.strip())

        # Call the super method
        return super(BaseModel, self).clean_fields(exclude=exclude)

    # Meta class
    class Meta:
        abstract = True


# Base model for representing a person
class Person(BaseModel):
    # One to one field for the user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.CASCADE
    )

    # String representation
    def __str__(self):
        # Get the name
        name = self.full_name

        # Return the name or the email
        return name if name else self.email

    # Method to get the role type
    def can_view_report_for_couple(self, couple_id):
        raise NotImplementedError

    # Method to get the user email
    @property
    def email(self):
        return self.user.email

    # Method to get the full name
    @property
    def full_name(self):
        return self.user.get_full_name()

    # Meta class
    class Meta:
        abstract = True


# Homebuyer model
class Homebuyer(Person, ValidateCategoryCoupleMixin):
    # Foreign key for the couple
    couple = models.ForeignKey(
        "core.Couple", verbose_name="Couple", on_delete=models.CASCADE
    )

    # Many to many field for the categories
    categories = models.ManyToManyField(
        "categories.Category",
        through="categories.CategoryWeight",
        verbose_name="Categories",
    )

    # String representation
    def __str__(self):
        return self.full_name

    # Method to get the role type
    @property
    def role_type(self):
        return "Homebuyer"

    # Method to check if the user can view the report for the couple
    def can_view_report_for_couple(self, couple_id):
        return self.couple_id == couple_id

    # Method to clean the fields
    def clean(self):
        # If the user is a realtor
        if hasattr(self.user, "realtor"):
            # Raise a validation error
            raise ValidationError(
                f"{self.user} is already a Realtor, cannot also have a Homebuyer relation."
            )

        # No more than 2 homebuyers per couple.
        homebuyers = set(
            self.couple.homebuyer_set.values_list("id", flat=True).distinct()
        )

        # Add the id to the homebuyers
        homebuyers.add(self.id)

        # If the length of the homebuyers is greater than 2
        if len(homebuyers) > 2:
            # Raise a validation error
            raise ValidationError("Couple already has 2 Homebuyers.")

        # Validate the categories and couples
        self._validate_categories_and_couples()

        # Call the super method
        return super(Homebuyer, self).clean()

    # Method to get the partner
    @property
    def partner(self):
        # Get the related homebuyers for the couple
        related_homebuyers = self.couple.homebuyer_set.exclude(id=self.id)

        # If the related homebuyers count is greater than 1
        if related_homebuyers.count() > 1:
            # Raise an integrity error
            raise IntegrityError(
                f"Couple has too many related Homebuyers and should be resolved immediately. (Couple ID: {self.couple_id})"
            )

        # Return the first related homebuyer
        return related_homebuyers.first()

    # Method to check if the homebuyer is registered
    @property
    def registered(self):
        return True

    # Method to get the report url
    def report_url(self):
        return self.couple.report_url()

    # Meta class
    class Meta:
        # Set the fields to be ordered by
        ordering = ["user__email"]

        # Set the verbose names
        verbose_name = "Homebuyer"
        verbose_name_plural = "Homebuyers"


# Realtor model
class Realtor(Person):
    # Method to check if the user can view the report for the couple
    def can_view_report_for_couple(self, couple_id):
        return self.couple_set.filter(id=couple_id).exists()

    # Method to clean the fields
    def clean(self):
        # if the user is a homebuyer
        if hasattr(self.user, "homebuyer"):
            # Raise the validation error
            raise ValidationError(
                f"{self.user} is already a Homebuyer, cannot also have a Realtor relation."
            )

        # Call the super method
        return super(Realtor, self).clean()

    # Method to get the role type
    @property
    def role_type(self):
        return "Realtor"

    # Meta class
    class Meta:
        # Set the fields to be ordered by
        ordering = ["user__email"]

        # Set the verbose names
        verbose_name = "Realtor"
        verbose_name_plural = "Realtors"


# Couple model
class Couple(BaseModel):
    # Create a foreign key for the realtor
    realtor = models.ForeignKey(
        "core.Realtor", verbose_name="Realtor", on_delete=models.CASCADE
    )

    # String representation
    def __str__(self):
        return ", ".join((str(hb) if hb else "?" for hb in self._homebuyers()))

    # Method to get the homebuyers
    def _homebuyers(self):
        # Get the homebuyers
        homebuyers = self.homebuyer_set.order_by("id")

        # If the homebuyers are not set
        if not homebuyers:
            # Return none
            homebuyers = (None, None)

        # If only one homebuyer is set
        elif homebuyers.count() == 1:
            # Set the homebuyers to the first homebuyer and none
            homebuyers = (homebuyers.first(), None)

        # Return both the homebuyers
        return homebuyers

    # Method to get the homebuyers
    def report_url(self):
        # If the id is not set
        if not self.id:
            return None

        # Return the reverse url
        return reverse("report", kwargs={"couple_id": self.id})

    # Meta class
    class Meta:
        # Set the field to be ordered by
        ordering = ["realtor"]

        # Set the verbose names
        verbose_name = "Couple"
        verbose_name_plural = "Couples"
