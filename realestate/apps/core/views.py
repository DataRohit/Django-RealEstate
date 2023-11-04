import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import HttpResponse


from realestate.apps.core.models import (
    Category,
    CategoryWeight,
    Couple,
    Grade,
    House,
    Realtor,
    Homebuyer,
)
from realestate.apps.core.forms import EvalHouseForm, AddCategoryForm, EditCategoryForm
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
    template_name = "core/houseEval.html"

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
        context = {
            "couple": couple,
            "house": house,
            "graded": graded,
            "form": eval_form,
        }
        context.update(self._score_context())

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        homebuyer = Homebuyer.objects.filter(user_id=request.user.id)
        house = get_object_or_404(House.objects.filter(id=kwargs["house_id"]))

        id = request.POST["category"]
        score = request.POST["score"]

        category = Category.objects.get(id=id)

        grade, created = Grade.objects.update_or_create(
            homebuyer=homebuyer.first(),
            category=category,
            house=house,
            defaults={"score": int(score)},
        )

        response_data = {"id": str(id), "score": str(score)}

        return HttpResponse(json.dumps(response_data), content_type="application/json")


class ReportView(BaseView):
    template_name = "core/report.html"

    def _permission_check(self, request, role, *args, **kwargs):
        couple_id = int(kwargs.get("couple_id", 0))
        get_object_or_404(Couple, id=couple_id)
        return role.can_view_report_for_couple(couple_id)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})


class CategoryView(BaseView):
    _USER_TYPES_ALLOWED = User._HOMEBUYER_ONLY

    template_name = "core/categories.html"

    def _permission_check(self, request, role, *args, **kwargs):
        return True

    def _weight_context(self):
        weight_field = CategoryWeight._meta.get_field("weight")
        weight_choices = dict(weight_field.choices)
        min_weight = min(weight for weight in weight_choices)
        max_weight = max(weight for weight in weight_choices)
        min_choice = weight_choices[min_weight]
        max_choice = weight_choices[max_weight]
        return {
            "min_weight": min_weight,
            "max_weight": max_weight,
            "min_choice": min_choice,
            "max_choice": max_choice,
            "default_weight": weight_field.default,
            "js_weight": json.dumps(weight_choices),
        }

    def get(self, request, *args, **kwargs):
        # Renders standard category page
        homebuyer = request.user.role_object
        couple = homebuyer.couple
        categories = Category.objects.filter(couple=couple)
        weights = CategoryWeight.objects.filter(homebuyer__user=request.user)

        weighted = []
        for category in categories:
            missing = True
            for weight in weights:
                if weight.category.id is category.id:
                    weighted.append((category, weight.weight))
                    missing = False
                    break
            if missing:
                weighted.append((category, None))

        context = {
            "weights": weighted,
            "form": AddCategoryForm(),
            "editForm": EditCategoryForm(),
        }
        context.update(self._weight_context())
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        homebuyer = request.user.role_object
        couple = homebuyer.couple
        summary = request.POST["summary"]
        description = request.POST["description"]

        # Updates a category
        if "category_id" in request.POST:
            category = get_object_or_404(Category, id=request.POST["category_id"])
            category.summary = summary
            category.description = description
            category.save()

        # Creates a category
        else:
            grade, created = Category.objects.update_or_create(
                couple=couple,
                summary=summary,
                defaults={"description": str(description)},
            )

        weights = CategoryWeight.objects.filter(homebuyer=homebuyer)
        categories = Category.objects.filter(couple=couple)

        weighted = []
        for category in categories:
            missing = True
            for weight in weights:
                if weight.category.id is category.id:
                    weighted.append((category, weight.weight))
                    missing = False
                    break
            if missing:
                weighted.append((category, None))

        context = {
            "weights": weighted,
            "form": AddCategoryForm(),
            "editForm": EditCategoryForm(),
        }
        context.update(self._weight_context())
        return render(request, self.template_name, context)
