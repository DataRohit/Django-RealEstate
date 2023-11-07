from django.db import models
from django.urls import reverse
from realestate.apps.core.models import BaseModel, ValidateCategoryCoupleMixin


class House(BaseModel, ValidateCategoryCoupleMixin):
    _NICKNAME_MIN_LENGTH = 1

    nickname = models.CharField(max_length=128, verbose_name="Nickname")
    address = models.TextField(blank=True, verbose_name="Address")

    couple = models.ForeignKey(
        "core.Couple", verbose_name="Couple", on_delete=models.CASCADE
    )
    categories = models.ManyToManyField(
        "categories.Category", through="categories.Grade", verbose_name="Categories"
    )

    def __str__(self):
        return self.nickname

    def clean(self):
        self._validate_categories_and_couples()
        return super(House, self).clean()

    def clean_fields(self, exclude=None):
        self._validate_min_length("nickname", self._NICKNAME_MIN_LENGTH)
        return super(House, self).clean_fields(exclude=exclude)

    def evaluation_url(self):
        return reverse("eval", kwargs={"house_id": self.id})

    class Meta:
        ordering = ["nickname"]
        unique_together = (("nickname", "couple"),)
        verbose_name = "House"
        verbose_name_plural = "Houses"
