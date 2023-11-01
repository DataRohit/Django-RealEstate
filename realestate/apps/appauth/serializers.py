from rest_framework import serializers
from django.utils.translation import gettext as _

from realestate.apps.core.models import House, Homebuyer, Couple


class APIUserSerializer(serializers.Serializer):
    def create(self, validated_data):
        return None

    def update(self, instance, validated_data):
        return None

    def validate(self, attrs):
        user = self.context["request"].user

        homebuyer = Homebuyer.objects.filter(user=user)

        if not homebuyer:
            msg = _("Only home buyers are allowed to use this functionality.")
            raise serializers.ValidationError(msg)
        return user
