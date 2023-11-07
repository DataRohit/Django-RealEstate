# Django imports
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# App imports
from realestate.apps.core.models import BaseModel


# Model for the categories
class Category(BaseModel):
    # Set the minimum length for the summary
    _SUMMARY_MIN_LENGTH = 1

    # Set the fields for the model
    summary = models.CharField(max_length=128, verbose_name="Summary")
    description = models.TextField(blank=True, verbose_name="Description")

    # Create a foreign key to the couple
    couple = models.ForeignKey(
        "core.Couple", verbose_name="Couple", on_delete=models.CASCADE
    )

    # String representation
    def __str__(self):
        return f"{self.summary} - {self.couple}"

    # Method to clean the fields
    def clean_fields(self, exclude=None):
        # Call the function to validate the minimum length
        self._validate_min_length("summary", self._SUMMARY_MIN_LENGTH)

        # Call the method from the parent class
        return super(Category, self).clean_fields(exclude=exclude)

    # Meta class
    class Meta:
        # Set field ordering
        ordering = ["summary"]

        # Set the unique together constraint
        unique_together = (("summary", "couple"),)

        # Set the verbose names
        verbose_name = "Category"
        verbose_name_plural = "Categories"


# Model for the category weights
class CategoryWeight(BaseModel):
    # Add the fields to the model
    weight = models.PositiveSmallIntegerField(
        choices=(
            (1, "Unimportant"),
            (2, "Below Average"),
            (3, "Average"),
            (4, "Above Average"),
            (5, "Important"),
        ),
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Weight",
    )

    # Create a foreign key to the homebuyer
    homebuyer = models.ForeignKey(
        "core.Homebuyer", verbose_name="Homebuyer", on_delete=models.CASCADE
    )

    # Create a foreign key to the category
    category = models.ForeignKey(
        "categories.Category", verbose_name="Category", on_delete=models.CASCADE
    )

    # String representation
    def __str__(self):
        return f"{self.homebuyer} gives {self.category} a weight of {self.weight}."

    # Method to clean the fields
    def clean(self):
        # Get the foreign key ids
        foreign_key_ids = (self.homebuyer_id, self.category_id)

        # If any of the foreign keys are None
        if not all(foreign_key_ids):
            # Raise a validation error
            raise ValidationError(
                "Homebuyer and Category must exist before saving a CategoryWeight instance."
            )

        # If the homebuyer and category are not for the same couple
        if self.homebuyer.couple_id != self.category.couple_id:
            # Raise a validation error
            raise ValidationError(
                f"Category '{self.category}' is for a different Homebuyer."
            )

        # Call the method from the parent class
        return super(CategoryWeight, self).clean()

    # Meta class
    class Meta:
        # Set the field ordering
        ordering = ["category", "homebuyer"]

        # Set the unique together constraint
        unique_together = (("homebuyer", "category"),)

        # Set the verbose names
        verbose_name = "Category Weight"
        verbose_name_plural = "Category Weights"


# Model for the grades
class Grade(BaseModel):
    # Add the fields to the model
    score = models.PositiveSmallIntegerField(
        choices=(
            (1, "Poor"),
            (2, "Below Average"),
            (3, "Average"),
            (4, "Above Average"),
            (5, "Excellent"),
        ),
        default=3,
        verbose_name="Score",
    )

    # Create a foreign key to the house
    house = models.ForeignKey(
        "house.House", verbose_name="House", on_delete=models.CASCADE
    )

    # Create a foreign key to the category
    category = models.ForeignKey(
        "categories.Category", verbose_name="Category", on_delete=models.CASCADE
    )

    # Create a foreign key to the homebuyer
    homebuyer = models.ForeignKey(
        "core.Homebuyer", verbose_name="Homebuyer", on_delete=models.CASCADE
    )

    # String representation
    def __str__(self):
        return f"{self.homebuyer.full_name} gives {str(self.house)} a score of {self.score} for category: '{str(self.category)}'"

    # Method to clean the fields
    def clean(self):
        # Get the foreign key ids
        foreign_key_ids = (self.house_id, self.category_id, self.homebuyer_id)

        # If any of the foreign keys are None
        if not all(foreign_key_ids):
            # Raise a validation error
            raise ValidationError(
                "House, Category, and Homebuyer must all exist before saving a Grade instance."
            )

        # Get the unique couple ids
        couple_ids = set(
            [self.house.couple_id, self.category.couple_id, self.homebuyer.couple_id]
        )

        # If the length of the unique couple ids is greater than 1
        if len(couple_ids) > 1:
            # Raise a validation error
            raise ValidationError(
                "House, Category, and Homebuyer must all be for the same Couple."
            )

        # Call the method from the parent class
        return super(Grade, self).clean()

    class Meta:
        ordering = ["homebuyer", "house", "category", "score"]
        unique_together = (("house", "category", "homebuyer"),)
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
