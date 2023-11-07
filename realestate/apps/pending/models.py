# Django imports
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.crypto import hashlib


# App imports
from realestate.apps.core.models import BaseModel
from realestate.apps.core.models import Couple
from realestate.apps.core.models import Homebuyer


# Function to generate a registration token
def _generate_registration_token():
    while True:
        token = hashlib.sha256(get_random_string(length=64).encode()).hexdigest()
        if not PendingHomebuyer.objects.filter(registration_token=token):
            return token


# PendingCouple model
class PendingCouple(BaseModel):
    # Create a foreign key to the Realtor model
    realtor = models.ForeignKey(
        "core.Realtor", verbose_name="Realtor", on_delete=models.CASCADE
    )

    # String representation
    def __str__(self):
        pending_homebuyers = self.pendinghomebuyer_set.all()

        if pending_homebuyers:
            return ", ".join(map(str, pending_homebuyers))
        return "No homebuyers specified"

    # Method to get the couple
    @property
    def couple(self):
        # Get the emails of the pending homebuyers
        emails = self.pendinghomebuyer_set.values_list("email", flat=True)

        # Get the homebuyers and couples
        homebuyers = Homebuyer.objects.filter(user__email__in=emails)
        couples = Couple.objects.filter(homebuyer__in=homebuyers)

        # If the couple exists, return it
        if couples.exists():
            return couples.first()

        # Otherwise, return None
        return None

    # Method to check if the couple is registered
    @property
    def registered(self):
        # Get the pending homebuyers
        pending_homebuyers = self.pendinghomebuyer_set.all()

        # Check if the homebuyers are registered
        return pending_homebuyers.count() == 2 and all(
            map(lambda hb: hb.registered, pending_homebuyers)
        )

    # Meta class
    class Meta:
        # Set field to be used for ordering
        ordering = ["realtor"]

        # Set the verbose names
        verbose_name = "Pending Couple"
        verbose_name_plural = "Pending Couples"


# PendingHomebuyer model
class PendingHomebuyer(BaseModel):
    # Set a constant for the email invite message
    _HOMEBUYER_INVITE_MESSAGE = """
        Hello,
        
        You have been invited to the Real Estate app.
        Register at the following link:
            {signup_link}
    """

    # Add the fields to the model
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

    # Create a foreign key to the PendingCouple model
    pending_couple = models.ForeignKey(
        "pending.PendingCouple", verbose_name="Pending Couple", on_delete=models.CASCADE
    )

    # String representation
    def __str__(self):
        return f"{self.email} ({self.registration_status})"

    # Method to get the signup link
    def _signup_link(self, host):
        url = reverse(
            "homebuyer-signup", kwargs={"registration_token": self.registration_token}
        )
        return host + url

    # Method to clean the model
    def clean(self):
        # Get the pending homebuyers
        pending_homebuyers = set(
            self.pending_couple.pendinghomebuyer_set.values_list(
                "id", flat=True
            ).distinct()
        )

        # Add the current pending homebuyer
        pending_homebuyers.add(self.id)

        # If the couple pending homebuyers is greater than 2
        if len(pending_homebuyers) > 2:
            # Raise the validation error
            raise ValidationError("PendingCouple already has 2 Homebuyers.")

        # Call the parent clean method
        return super(PendingHomebuyer, self).clean()

    # Method to get the couple
    @property
    def couple(self):
        return self.pending_couple.couple

    # Method to get the partner
    @property
    def partner(self):
        # Get the pending homebuyers
        pending_homebuyers = self.pending_couple.pendinghomebuyer_set.exclude(
            id=self.id
        )

        # If the pending homebuyers is greater than 1
        if pending_homebuyers.count() > 1:
            # Raise the integrity error
            raise IntegrityError(
                f"PendingCouple has too many related PendingHomebuyer and should be resolved immediately. (PendingCouple ID: {self.pending_couple.id})"
            )

        # Else return the first member of the pending homebuyers
        return pending_homebuyers.first()

    # Method to check if the homebuyer is registered
    @property
    def registered(self):
        if Homebuyer.objects.filter(user__email=self.email).exists():
            return True

    # Method to get the registration status
    @property
    def registration_status(self):
        return "Registered" if self.registered else "Unregistered"

    # Method to send the email invite
    def send_email_invite(self, request):
        # If the homebuyer is registered, return None
        if self.registered:
            return None

        # Get the message text
        message = self._HOMEBUYER_INVITE_MESSAGE.format(
            signup_link=self._signup_link(request.get_host())
        )

        # Send the email
        return send_mail(
            "Real Estate Invite",
            message,
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=False,
        )

    # Meta class
    class Meta:
        # Set the fields to be used for ordering
        ordering = ["email"]

        # Set the verbose names
        verbose_name = "Pending Homebuyer"
        verbose_name_plural = "Pending Homebuyers"
