# Imports
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# List of models to import when using the asterisk (*) wildcard in an import
__all__ = [
    "Category",
    "CategoryWeight",
    "Couple",
    "Grade",
    "Homebuyer",
    "House",
    "Realtor",
]


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        "auth.User", verbose_name="User", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.user.username

    class Meta:
        abstract = True


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    summary = models.CharField(max_length=128, verbose_name="Summary")
    description = models.TextField(blank=True, verbose_name="Description")
    couple = models.ForeignKey(
        "core.Couple", verbose_name="Couple", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.summary

    class Meta:
        ordering = ["summary"]
        unique_together = [("summary", "couple")]
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class CategoryWeight(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    weight = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(0), MaxValueValidator(100)),
        help_text="0-100",
        verbose_name="Weight",
    )
    homebuyer = models.ForeignKey(
        "core.Homebuyer", verbose_name="Homebuyer", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        "core.Category", verbose_name="Category", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.homebuyer} gives {self.category} a weight of {self.weight}."

    def clean(self, *args, **kwargs):
        if self.homebuyer.couple_id != self.category.couple_id:
            raise ValidationError(
                f"Category {self.category} is for a different Homebuyer couple."
            )

    class Meta:
        ordering = ["homebuyer", "category"]
        unique_together = [("homebuyer", "category")]
        verbose_name = "Category Weight"
        verbose_name_plural = "Category Weights"


class Couple(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    realtor = models.ForeignKey(
        "core.Realtor", verbose_name="Realtor", on_delete=models.CASCADE
    )

    def __str__(self):
        username = "user__username"
        homebuyers = self.homebuyer_set.values_list(username, flat=True).order_by(
            username
        )

        if not homebuyers:
            homebuyers = ["?", "?"]

        elif homebuyers.count() == 1:
            homebuyers = [homebuyers.first(), "?"]

        return " and ".join(homebuyers)

    class Meta:
        ordering = ["realtor"]
        verbose_name = "Couple"
        verbose_name_plural = "Couples"


class Grade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    score = models.PositiveSmallIntegerField(
        choices=((1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")),
        default=3,
        verbose_name="Score",
    )

    house = models.ForeignKey(
        "core.House", verbose_name="House", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        "core.Category", verbose_name="Category", on_delete=models.CASCADE
    )
    homebuyer = models.ForeignKey(
        "core.Homebuyer", verbose_name="Homebuyer", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.homebuyer} gives {self.house} a {self.score} for category {self.category}."

    def clean(self, *args, **kwargs):
        if (self.house_couple_id != self.category.couple_id) or (
            self.category.couple_id != self.homebuyer.couple_id
        ):
            raise ValidationError(
                f"House, Category, and Homebuyer must be for the same Couple."
            )

    class Meta:
        ordering = ["homebuyer", "house", "category", "score"]
        unique_together = [("house", "category", "homebuyer")]
        verbose_name = "Grade"
        verbose_name_plural = "Grades"


class Homebuyer(Person):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.OneToOneField(
        "core.Homebuyer",
        blank=True,
        null=True,
        verbose_name="Partner",
        on_delete=models.CASCADE,
    )
    couple = models.ForeignKey(
        "core.Couple", verbose_name="Couple", on_delete=models.CASCADE
    )
    categories = models.ManyToManyField(
        "core.Category",
        through="core.CategoryWeight",
        verbose_name="Categories",
    )

    def clean(self, *args, **kwargs):
        super(Homebuyer, self).clean(*args, **kwargs)

    class Meta:
        ordering = ["user__username"]
        verbose_name = "Homebuyer"
        verbose_name_plural = "Homebuyers"


class House(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nickname = models.CharField(max_length=128, verbose_name="Nickname")
    address = models.TextField(blank=True, verbose_name="Address")

    couple = models.ForeignKey(
        "core.Couple", verbose_name="Couple", on_delete=models.CASCADE
    )
    categories = models.ManyToManyField(
        "core.Category", through="core.Grade", verbose_name="Categories"
    )

    def clean(self, *args, **kwargs):
        super(Homebuyer, self).clean(*args, **kwargs)

    def __str__(self):
        return self.nickname

    class Meta:
        ordering = ["nickname"]
        unique_together = [("nickname", "couple")]
        verbose_name = "House"
        verbose_name_plural = "Houses"


class Realtor(Person):
    class Meta:
        ordering = ["user__username"]
        verbose_name = "Realtor"
        verbose_name_plural = "Realtors"
