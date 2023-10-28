from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import uuid

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
    """
    Abstract model class representing information that is common to both
    Homebuyer and Realtor.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        "auth.User", verbose_name="User", on_delete=models.CASCADE
    )

    def __unicode__(self):
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

    class Meta:
        verbose_name = "Category Weight"
        verbose_name_plural = "Category Weights"


class Couple(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    realtor = models.ForeignKey(
        "core.Realtor", verbose_name="Realtor", on_delete=models.CASCADE
    )

    def __str__(self):
        return ", ".join(self.homebuyer_set.values_list("user__username", flat=True))

    class Meta:
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

    class Meta:
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

    class Meta:
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

    def __unicode__(self):
        return self.nickname

    class Meta:
        verbose_name = "House"
        verbose_name_plural = "Houses"


class Realtor(Person):
    class Meta:
        verbose_name = "Realtor"
        verbose_name_plural = "Realtors"
