import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.urls import reverse


__all__ = [
    "BaseModel",
    "Person",
    "Homebuyer",
    "Realtor",
    "Couple",
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

    def can_view_report_for_couple(self, couple_id):
        raise NotImplementedError

    @property
    def email(self):
        return self.user.email

    @property
    def full_name(self):
        return self.user.get_full_name()

    class Meta:
        abstract = True


class Homebuyer(Person, ValidateCategoryCoupleMixin):
    couple = models.ForeignKey(
        "core.Couple", verbose_name="Couple", on_delete=models.CASCADE
    )
    categories = models.ManyToManyField(
        "categories.Category",
        through="categories.CategoryWeight",
        verbose_name="Categories",
    )

    def __str__(self):
        return self.full_name

    @property
    def role_type(self):
        return "Homebuyer"

    def can_view_report_for_couple(self, couple_id):
        return self.couple_id == couple_id

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

    def report_url(self):
        return self.couple.report_url()

    class Meta:
        ordering = ["user__email"]
        verbose_name = "Homebuyer"
        verbose_name_plural = "Homebuyers"


class Realtor(Person):
    def can_view_report_for_couple(self, couple_id):
        return self.couple_set.filter(id=couple_id).exists()

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


class Couple(BaseModel):
    realtor = models.ForeignKey(
        "core.Realtor", verbose_name="Realtor", on_delete=models.CASCADE
    )

    def __str__(self):
        return ", ".join((str(hb) if hb else "?" for hb in self._homebuyers()))

    def _homebuyers(self):
        homebuyers = self.homebuyer_set.order_by("id")

        if not homebuyers:
            homebuyers = (None, None)
        elif homebuyers.count() == 1:
            homebuyers = (homebuyers.first(), None)
        return homebuyers

    def report_url(self):
        if not self.id:
            return None
        return reverse("report", kwargs={"couple_id": self.id})

    class Meta:
        ordering = ["realtor"]
        verbose_name = "Couple"
        verbose_name_plural = "Couples"
