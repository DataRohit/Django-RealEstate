# Django imports
from django.db import models
from django.urls import reverse


# App imports
from realestate.apps.core.models import BaseModel
from realestate.apps.core.models import ValidateCategoryCoupleMixin


# House Model
class House(BaseModel, ValidateCategoryCoupleMixin):
    # Set the minimum length for the nickname
    _NICKNAME_MIN_LENGTH = 1

    # Fields for the model
    nickname = models.CharField(max_length=128, verbose_name="Nickname")
    address = models.TextField(blank=True, verbose_name="Address")

    # Foreign key relation to the couple
    couple = models.ForeignKey(
        "core.Couple", verbose_name="Couple", on_delete=models.CASCADE
    )

    # Many to many relation to the categories
    categories = models.ManyToManyField(
        "categories.Category", through="categories.Grade", verbose_name="Categories"
    )

    # String representation
    def __str__(self):
        return self.nickname

    # Method to clean the model
    def clean(self):
        # Validate the categories and couples
        self._validate_categories_and_couples()

        # Return the cleaned data
        return super(House, self).clean()

    # Method to clean the fields
    def clean_fields(self, exclude=None):
        # Validate the minimum length of the nickname
        self._validate_min_length("nickname", self._NICKNAME_MIN_LENGTH)

        # Call the super method
        return super(House, self).clean_fields(exclude=exclude)

    # Method to get the evaluation url
    def evaluation_url(self):
        return reverse("house-eval", kwargs={"house_id": self.id})

    # Method to get the evaluation url
    class Meta:
        # Set the fields for ordering and unique together
        ordering = ["nickname"]
        unique_together = (("nickname", "couple"),)

        # Set the verbose names
        verbose_name = "House"
        verbose_name_plural = "Houses"
