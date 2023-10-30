from django.contrib.auth.models import User
from django.db import models, IntegrityError
from django.utils.crypto import get_random_string, hashlib
from django.core.exceptions import ValidationError

from realestate.apps.core.models import BaseModel


# Create your models here.
def _generate_registration_token():
    while True:
        token = hashlib.sha256(get_random_string(length=64)).hexdigest()
        if not PendingHomebuyer.objects.filter(registration_token=token):
            return token


class PendingCouple(BaseModel):
    realtor = models.ForeignKey(
        "core.Realtor", verbose_name="Realtor", on_delete=models.CASCADE
    )

    def __str__(self):
        homebuyer_string = "No homebuyers specified"

        pending_homebuyers = self.pendinghomebuyer_set.order_by("email")

        if pending_homebuyers:
            homebuyer_string = ", ".join(map(str, pending_homebuyers))

        return f"{self.realtor}: {homebuyer_string}"

    class Meta:
        ordering = ["realtor"]
        verbose_name = "Pending Couple"
        verbose_name_plural = "Pending Couples"


class PendingHomebuyer(BaseModel):
    email = models.EmailField(max_length=75, unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=30, verbose_name="First Name")
    last_name = models.CharField(max_length=30, verbose_name="Last Name")

    registration_token = models.CharField(
        max_length=64,
        default=_generate_registration_token,
        editable=False,
        unique=True,
        verbose_name="Registration Token",
    )
    pending_couple = models.ForeignKey(
        "pending.PendingCouple", verbose_name="Pending Couple", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.email} ({self.registration_status})"

    def clean(self):
        pending_homebuyers = set(
            self.pending_couple.pendinghomebuyer_set.values_list(
                "id", flat=True
            ).distinct()
        )
        pending_homebuyers.add(self.id)

        if len(pending_homebuyers) > 2:
            raise ValidationError("PendingCouple already has 2 Homebuyers.")

        return super(PendingHomebuyer, self).clean()

    @property
    def partner(self):
        pending_homebuyers = self.pending_couple.pendinghomebuyer_set.exclude(
            id=self.id
        )
        if pending_homebuyers.count() > 1:
            raise IntegrityError(
                f"PendingCouple has too many related PendingHomebuyer and should be resolved immediately. (PendingCouple ID: {self.pending_couple.id})"
            )
        return pending_homebuyers.first()

    @property
    def registered(self):
        if User.objects.filter(email=self.email).exists():
            return True
        return False

    @property
    def registration_status(self):
        return "Registered" if self.registered else "Unregistered"

    class Meta:
        ordering = ["email"]
        verbose_name = "Pending Homebuyer"
        verbose_name_plural = "Pending Homebuyers"
