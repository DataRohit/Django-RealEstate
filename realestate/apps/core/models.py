import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError, models

__all__ = [
    "BaseModel",
    "Category",
    "CategoryWeight",
    "Couple",
    "Grade",
    "Homebuyer",
    "House",
    "Realtor",
]


class ValidateCategoryCoupleMixin(object):
    def _validate_categories_and_couples(self):
        if not self.pk:
            return

        category_couple_ids = set(self.categories.values_list("couple", flat=True))
        if category_couple_ids:
            if (
                len(category_couple_ids) > 1
                or self.couple_id not in category_couple_ids
            ):
                raise ValidationError("Invalid categories for this couple.")
        return


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def _validate_min_length(self, fieldname, min_length):
        field = getattr(self, fieldname, "")
        if not field or len(field) < min_length:
            raise ValidationError(
                {fieldname: [f"{fieldname} must be at least length {min_length}"]}
            )
        return

    def clean_fields(self, exclude=None):
        for field in self._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):
                fieldname = field.name
                value = getattr(self, fieldname)
                if value:
                    setattr(self, fieldname, value.strip())
        return super(BaseModel, self).clean_fields(exclude=exclude)

    class Meta:
        abstract = True


class Person(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.CASCADE
    )

    def __str__(self):
        name = self.full_name
        return name if name else self.email

    @property
    def email(self):
        return self.user.email

    @property
    def full_name(self):
        return self.user.get_full_name()

    class Meta:
        abstract = True


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
        validators=[MinValueValidator(0), MaxValueValidator(100)],
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


class Couple(BaseModel):
    realtor = models.ForeignKey(
        "core.Realtor", verbose_name="Realtor", on_delete=models.CASCADE
    )

    def __str__(self):
        return ", ".join((str(hb) if hb else "?" for hb in self._homebuyers()))

    def _homebuyers(self):
        homebuyers = self.homebuyer_set.order_by("id")

        if homebuyers.count() == 0:
            return "Couple (no homebuyers)"
        elif homebuyers.count() == 1:
            return f"Couple (1 homebuyer: {homebuyers.first()})"
        elif homebuyers.count() == 2:
            return f"Couple (2 homebuyers: {homebuyers.first()}, {homebuyers.last()})"

    class Meta:
        ordering = ["realtor"]
        verbose_name = "Couple"
        verbose_name_plural = "Couples"


class Grade(BaseModel):
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


class Homebuyer(Person, ValidateCategoryCoupleMixin):
    couple = models.ForeignKey(
        "core.Couple", verbose_name="Couple", on_delete=models.CASCADE
    )
    categories = models.ManyToManyField(
        "core.Category", through="core.CategoryWeight", verbose_name="Categories"
    )

    def __str__(self):
        return self.full_name

    @property
    def role_type(self):
        return "Homebuyer"

    def clean(self):
        if hasattr(self.user, "realtor"):
            raise ValidationError(
                f"{self.user} is already a Realtor, cannot also have a Homebuyer relation."
            )
        # No more than 2 homebuyers per couple.
        homebuyers = set(
            self.couple.homebuyer_set.values_list("id", flat=True).distinct()
        )
        homebuyers.add(self.id)
        if len(homebuyers) > 2:
            raise ValidationError("Couple already has 2 Homebuyers.")

        self._validate_categories_and_couples()
        return super(Homebuyer, self).clean()

    @property
    def partner(self):
        related_homebuyers = self.couple.homebuyer_set.exclude(id=self.id)
        if related_homebuyers.count() > 1:
            raise IntegrityError(
                f"Couple has too many related Homebuyers and should be resolved immediately. (Couple ID: {self.couple_id})"
            )
        return related_homebuyers.first()

    class Meta:
        ordering = ["user__email"]
        verbose_name = "Homebuyer"
        verbose_name_plural = "Homebuyers"


class House(BaseModel, ValidateCategoryCoupleMixin):
    _NICKNAME_MIN_LENGTH = 1

    nickname = models.CharField(max_length=128, verbose_name="Nickname")
    address = models.TextField(blank=True, verbose_name="Address")

    couple = models.ForeignKey(
        "core.Couple", verbose_name="Couple", on_delete=models.CASCADE
    )
    categories = models.ManyToManyField(
        "core.Category", through="core.Grade", verbose_name="Categories"
    )

    def __str__(self):
        return self.nickname

    def clean(self):
        self._validate_categories_and_couples()
        return super(House, self).clean()

    def clean_fields(self, exclude=None):
        self._validate_min_length("nickname", self._NICKNAME_MIN_LENGTH)
        return super(House, self).clean_fields(exclude=exclude)

    class Meta:
        ordering = ["nickname"]
        unique_together = (("nickname", "couple"),)
        verbose_name = "House"
        verbose_name_plural = "Houses"


class Realtor(Person):
    def clean(self):
        if hasattr(self.user, "homebuyer"):
            raise ValidationError(
                f"{self.user} is already a Homebuyer, cannot also have a Realtor relation."
            )
        return super(Realtor, self).clean()

    @property
    def role_type(self):
        return "Realtor"

    class Meta:
        ordering = ["user__email"]
        verbose_name = "Realtor"
        verbose_name_plural = "Realtors"
