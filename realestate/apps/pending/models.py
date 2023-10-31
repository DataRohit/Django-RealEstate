from urllib.parse import urlencode

from django.conf import settings
from django.db import models, IntegrityError
from django.utils.crypto import get_random_string, hashlib
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse

from realestate.apps.core.models import BaseModel, Couple, Homebuyer


# Create your models here.
def _generate_registration_token():
    while True:
        token = hashlib.sha256(get_random_string(length=64).encode()).hexdigest()
        if not PendingHomebuyer.objects.filter(registration_token=token):
            return token


class PendingCouple(BaseModel):
    realtor = models.ForeignKey(
        "core.Realtor", verbose_name="Realtor", on_delete=models.CASCADE
    )

    def __str__(self):
        pending_homebuyers = self.pendinghomebuyer_set.all()

        if pending_homebuyers:
            return ", ".join(map(str, pending_homebuyers))
        return "No homebuyers specified"

    @property
    def couple(self):
        emails = self.pendinghomebuyer_set.values_list("email", flat=True)
        homebuyers = Homebuyer.objects.filter(user__email__in=emails)
        couples = Couple.objects.filter(homebuyer__in=homebuyers)

        if couples.exists():
            return couples.first()
        return None

    class Meta:
        ordering = ["realtor"]
        verbose_name = "Pending Couple"
        verbose_name_plural = "Pending Couples"


class PendingHomebuyer(BaseModel):
    _HOMEBUYER_INVITE_MESSAGE = """
        Hello,
        
        You have been invited to the Real Estate app.
        Register at the following link:
            {signup_link}
    """

    email = models.EmailField(
        unique=True,
        verbose_name="Email Address",
        error_messages={"unique": ("A user with this email already exists.")},
    )
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

    def _signup_link(self, host):
        url = reverse("signup", kwargs={"registration_token": self.registration_token})
        return host + url

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
    def couple(self):
        return self.pending_couple.couple

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
        if Homebuyer.objects.filter(user__email=self.email).exists():
            return True

    @property
    def registration_status(self):
        return "Registered" if self.registered else "Unregistered"

    def send_email_invite(self, request):
        if self.registered:
            return None

        message = self._HOMEBUYER_INVITE_MESSAGE.format(
            signup_link=self._signup_link(request.get_host())
        )

        return send_mail(
            "Real Estate Invite",
            message,
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=False,
        )

    class Meta:
        ordering = ["email"]
        verbose_name = "Pending Homebuyer"
        verbose_name_plural = "Pending Homebuyers"
