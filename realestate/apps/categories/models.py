# Django imports
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db import transaction
from django.dispatch import receiver


# App imports
from realestate.apps.core.models import BaseModel
from realestate.apps.core.models import Couple
from realestate.apps.core.models import Homebuyer
from realestate.apps.house.models import House


# Categories for a new couple
_CATEGORIES = {
    "comfort": {
        "summary": "Comfort",
        "description": "Comfort assesses how cozy and livable a house is. It considers factors such as the layout, interior design, temperature control, and the quality of furnishings. A higher comfort rating typically indicates a more pleasant and inviting living environment.",
    },
    "location": {
        "summary": "Location",
        "description": (
            "Location evaluates the accessibility and convenience of the property's surroundings. This category takes into account proximity to essential amenities such as schools, shopping centers, parks, and public transportation. A higher location rating suggests a more desirable and well-situated property."
        ),
    },
    "maintenance": {
        "summary": "Maintenance",
        "description": (
            "Maintenance assesses the overall condition and upkeep of the house. It includes the state of the building structure, the functionality of appliances, and the quality of landscaping. A higher maintenance rating indicates that the property is well-maintained and likely to require fewer repairs or renovations."
        ),
    },
}


# Create default categories
_DEFAULT_CATEGORIES = [
    _CATEGORIES["comfort"],
    _CATEGORIES["location"],
    _CATEGORIES["maintenance"],
]


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


# Create a post save receiver to add default categories
@receiver(models.signals.post_save)
def _add_default_categories(sender, instance, created, **kwargs):
    # If a new couple is created
    if created and sender == Couple:
        # Get the couple
        couple = instance

        # Create a list of categories
        categories = [
            Category(couple_id=couple.id, **category_data)
            for category_data in _DEFAULT_CATEGORIES
        ]

        # Create a database transaction
        with transaction.atomic():
            # Bulk create the categories
            created_categories = Category.objects.bulk_create(categories)

            # Get the homebuyers
            homebuyers = couple.homebuyer_set.all()

            # Create category weights
            category_weights = [
                CategoryWeight(category=category, homebuyer=homebuyer)
                for category in created_categories
                for homebuyer in homebuyers
            ]

            # Bulk create the category weights
            CategoryWeight.objects.bulk_create(category_weights)

    # Return
    return


# Create a post save receiver to add default grades and weights
@receiver(models.signals.post_save)
def _add_default_weights_and_grades(sender, instance, created, **kwargs):
    # List to store the homebuyers
    homebuyers = []

    # If a new homebuyer is created
    if sender == Homebuyer:
        # Update the homebuyers list
        homebuyers = [instance]

    # If a new house or category is created
    elif sender in [Category, House]:
        # Get the homebuyers
        homebuyers = instance.couple.homebuyer_set.all()

    # Create a database transaction
    with transaction.atomic():
        # Traverse the homebuyers
        for homebuyer in homebuyers:
            # Get the unweighted categories
            unweighted_categories = homebuyer.unweighted_categories()

            # If unweighted categories exist
            if unweighted_categories:
                # Map the categories to category weights
                category_weights = map(
                    lambda category: CategoryWeight(
                        category=category, homebuyer=homebuyer
                    ),
                    unweighted_categories,
                )

                # Bulk create the category weights
                CategoryWeight.objects.bulk_create(category_weights)

            # Get the unevaluated houses
            ungraded_house_categories = homebuyer.ungraded_house_categories()

            # If unevaluated houses exist
            if ungraded_house_categories:
                # Function to map the house categories to grades
                def _grade_mapper(house_category):
                    house, category = house_category
                    return Grade(house=house, category=category, homebuyer=homebuyer)

                # Map the ungraded house categories to grades
                grades = map(_grade_mapper, ungraded_house_categories)

                # Bulk create the grades
                Grade.objects.bulk_create(grades)
    # Return
    return
