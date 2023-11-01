from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.generic import View
from django import forms
from django.contrib import messages


from realestate.apps.core.models import (
    Category,
    Couple,
    Grade,
    House,
    Homebuyer,
    Realtor,
)
from realestate.apps.appauth.models import User


class BaseView(View):
    _USER_TYPES_ALLOWED = User._ALL_TYPES_ALLOWED

    def _permission_check(self, request, role_type, *args, **kwargs):
        return True

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        role_type = request.user.role_object.role_type
        if role_type in self._USER_TYPES_ALLOWED:
            if self._permission_check(request, role_type, *args, **kwargs):
                return super(BaseView, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied


class HomeView(BaseView):
    def get(self, request, *args, **kwargs):
        if Realtor.objects.filter(user=request.user).exists():
            return render(request, "core/realtorHome.html")

        couple = Couple.objects.filter(homebuyer__user=request.user).first()
        house = House.objects.filter(couple=couple)
        return render(
            request, "core/homebuyerHome.html", {"couple": couple, "house": house}
        )


class EvalView(BaseView):
    def _permission_check(self, request, role, *args, **kwargs):
        if role.role_type == "Homebuyer":
            house_id = kwargs.get("house_id", None)
            if role.couple.house_set.filter(id=house_id).exists():
                return True
        return False

    def get(self, request, *args, **kwargs):
        homebuyer = request.user.role_object
        couple = Couple.objects.filter(homebuyer__user=request.user)
        categories = Category.objects.filter(couple=couple)
        house = get_object_or_404(House.objects.filter(id=kwargs["house_id"]))
        grades = Grade.objects.filter(house=house, homebuyer=homebuyer)

        graded = []
        for category in categories:
            missing = True
            for grade in grades:
                if grade.category.id is category.id:
                    graded.append((category, grade.score))
                    missing = False
                    break
            if missing:
                graded.append((category, None))

        class ContactForm(forms.Form):
            def __init__(self, *args, **kwargs):
                super(ContactForm, self).__init__(*args, **kwargs)
                for c, s in graded:
                    self.fields[str(c.id)] = forms.CharField(
                        initial="3" if None else s, widget=forms.HiddenInput()
                    )

        context = {
            "couple": couple,
            "house": house,
            "grades": graded,
            "form": ContactForm(),
        }
        return render(request, "core/houseEval.html", context)

    def post(self, request, *args, **kwargs):
        homebuyer = Homebuyer.objects.filter(user_id=request.user.id)
        couple = Couple.objects.filter(homebuyer__user=request.user)
        categories = Category.objects.filter(couple=couple)
        house = get_object_or_404(House.objects.filter(id=kwargs["house_id"]))

        for category in categories:
            value = request.POST.get(str(category.id))
            if not value:
                value = 3
            grade, created = Grade.objects.update_or_create(
                homebuyer=homebuyer.first(),
                category=category,
                house=house,
                defaults={"score": int(value)},
            )

        grades = Grade.objects.filter(house=house, homebuyer=homebuyer)

        graded = []
        for category in categories:
            missing = True
            for grade in grades:
                if grade.category.id is category.id:
                    graded.append((category, grade.score))
                    missing = False
                    break
            if missing:
                graded.append((category, None))

        class ContactForm(forms.Form):
            def __init__(self, *args, **kwargs):
                super(ContactForm, self).__init__(*args, **kwargs)
                for c, s in graded:
                    self.fields[str(c.id)] = forms.CharField(
                        initial="0" if None else s, widget=forms.HiddenInput()
                    )

        messages.success(request, "Your evaluation was saved!")

        context = {
            "couple": couple,
            "house": house,
            "grades": graded,
            "form": ContactForm(),
        }
        return render(request, "core/houseEval.html", context)
