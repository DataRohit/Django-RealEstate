import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib import messages


from realestate.apps.core.models import (
    Category,
    Couple,
    Grade,
    House,
    Homebuyer,
    Realtor,
)
from realestate.apps.core.forms import EvalHouseForm
from realestate.apps.appauth.models import User


class BaseView(View):
    _USER_TYPES_ALLOWED = User._ALL_TYPES_ALLOWED

    def _permission_check(self, request, role, *args, **kwargs):
        return True

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        role = request.user.role_object
        if role.role_type in self._USER_TYPES_ALLOWED:
            if self._permission_check(request, role, *args, **kwargs):
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

    def _score_context(self):
        score_field = Grade._meta.get_field("score")
        score_choices = dict(score_field.choices)
        min_score = min(score for score in score_choices)
        max_score = max(score for score in score_choices)
        min_choice = score_choices[min_score]
        max_choice = score_choices[max_score]
        return {
            "min_score": min_score,
            "max_score": max_score,
            "min_choice": min_choice,
            "max_choice": max_choice,
            "default_score": score_field.default,
            "js_scores": json.dumps(score_choices),
        }

    def get(self, request, *args, **kwargs):
        homebuyer = request.user.role_object

        house = get_object_or_404(House.objects.filter(id=kwargs["house_id"]))

        couple = Couple.objects.filter(homebuyer__user=request.user).first()
        categories = Category.objects.filter(couple__id=couple.id)

        grades = Grade.objects.filter(house=house, homebuyer=homebuyer)

        graded = {}
        for category in categories:
            missing = True
            for grade in grades:
                if grade.category.id == category.id:
                    graded[category] = grade.score
                    missing = False
                    break
            if missing:
                graded[category] = 3

        eval_form = EvalHouseForm(extra_fields=graded, categories=categories)
        context = {"house": house, "form": eval_form}
        context.update(self._score_context())

        return render(request, "core/houseEval.html", context)

    def post(self, request, *args, **kwargs):
        homebuyer = request.user.role_object

        house = get_object_or_404(House.objects.filter(id=kwargs["house_id"]))

        couple = Couple.objects.filter(homebuyer__user=request.user).first()
        categories = Category.objects.filter(couple__id=couple.id)

        for category in categories:
            value = request.POST.get(str(category))
            if not value:
                value = 3
            grade, created = Grade.objects.update_or_create(
                homebuyer=homebuyer,
                category=category,
                house=house,
                defaults={"score": int(value)},
            )

        grades = Grade.objects.filter(house=house, homebuyer=homebuyer)

        graded = {}
        for category in categories:
            missing = True
            for grade in grades:
                if grade.category.id == category.id:
                    graded[category] = grade.score
                    missing = False
                    break
            if missing:
                graded[category] = None

        eval_form = EvalHouseForm(extra_fields=graded, categories=categories)
        context = {"house": house, "form": eval_form}
        context.update(self._score_context())

        messages.success(request, "Your evaluation was saved!")

        return render(request, "core/houseEval.html", context)
