from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from realestate.apps.core.models import BaseModel


class Category(BaseModel):
    _SUMMARY_MIN_LENGTH = 1

    summary = models.CharField(max_length=128, verbose_name="Summary")
    description = models.TextField(blank=True, verbose_name="Description")

    couple = models.ForeignKey(
        "core.Couple", verbose_name="Couple", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.summary} - {self.couple}"

    def clean_fields(self, exclude=None):
        self._validate_min_length("summary", self._SUMMARY_MIN_LENGTH)
        return super(Category, self).clean_fields(exclude=exclude)

    class Meta:
        ordering = ["summary"]
        unique_together = (("summary", "couple"),)
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class CategoryWeight(BaseModel):
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
    homebuyer = models.ForeignKey(
        "core.Homebuyer", verbose_name="Homebuyer", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        "categories.Category", verbose_name="Category", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.homebuyer} gives {self.category} a weight of {self.weight}."

    def clean(self):
        foreign_key_ids = (self.homebuyer_id, self.category_id)
        if not all(foreign_key_ids):
            raise ValidationError(
                "Homebuyer and Category must exist before saving a CategoryWeight instance."
            )

        if self.homebuyer.couple_id != self.category.couple_id:
            raise ValidationError(
                f"Category '{self.category}' is for a different Homebuyer."
            )
        return super(CategoryWeight, self).clean()

    class Meta:
        ordering = ["category", "homebuyer"]
        unique_together = (("homebuyer", "category"),)
        verbose_name = "Category Weight"
        verbose_name_plural = "Category Weights"


class Grade(BaseModel):
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

    house = models.ForeignKey(
        "house.House", verbose_name="House", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        "categories.Category", verbose_name="Category", on_delete=models.CASCADE
    )
    homebuyer = models.ForeignKey(
        "core.Homebuyer", verbose_name="Homebuyer", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.homebuyer.full_name} gives {str(self.house)} a score of {self.score} for category: '{str(self.category)}'"

    def clean(self):
        foreign_key_ids = (self.house_id, self.category_id, self.homebuyer_id)
        if not all(foreign_key_ids):
            raise ValidationError(
                "House, Category, and Homebuyer must all exist before saving a Grade instance."
            )
        couple_ids = set(
            [self.house.couple_id, self.category.couple_id, self.homebuyer.couple_id]
        )
        if len(couple_ids) > 1:
            raise ValidationError(
                "House, Category, and Homebuyer must all be for the same Couple."
            )
        return super(Grade, self).clean()

    class Meta:
        ordering = ["homebuyer", "house", "category", "score"]
        unique_together = (("house", "category", "homebuyer"),)
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
