import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import redirect
from django.contrib import messages


from realestate.apps.core.models import (
    Category,
    CategoryWeight,
    Couple,
    Grade,
    House,
    Realtor,
    Homebuyer,
)
from realestate.apps.core.forms import (
    EvalHouseForm,
    CategoryWeightForm,
    HouseEditForm,
    HouseDeleteForm,
    CategoryAddForm,
)
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


class HouseEditView(BaseView):
    template_name = "core/houseEdit.html"

    def get(self, request, *args, **kwargs):
        house_id = kwargs.get("house_id", None)

        if house_id:
            house = get_object_or_404(House.objects.filter(id=house_id))
            if house.couple.homebuyer_set.filter(user=request.user).exists():
                house_form = HouseEditForm(
                    initial={"nickname": house.nickname, "address": house.address}
                )

                return render(
                    request, self.template_name, {"form": house_form, "house": house}
                )

        return redirect("home")

    def post(self, request, *args, **kwargs):
        house_id = kwargs.get("house_id", None)

        if house_id:
            house = get_object_or_404(House.objects.filter(id=house_id))
            if house.couple.homebuyer_set.filter(user=request.user).exists():
                house_form = HouseEditForm(request.POST)

                if house_form.is_valid():
                    house.nickname = house_form.cleaned_data["nickname"]
                    house.address = house_form.cleaned_data["address"]
                    house.save()

                    messages.success(request, "Your house has been updated!")

                    return redirect("house-edit", house_id=house.id)

                return render(
                    request, self.template_name, {"form": house_form, "house": house}
                )

        return redirect("home")


class HouseDeleteView(BaseView):
    template_name = "core/houseDelete.html"

    def get(self, request, *args, **kwargs):
        house_id = kwargs.get("house_id", None)

        if house_id:
            house = get_object_or_404(House.objects.filter(id=house_id))
            if house.couple.homebuyer_set.filter(user=request.user).exists():
                form = HouseDeleteForm(
                    initial={"nickname": house.nickname, "address": house.address}
                )
                return render(
                    request, self.template_name, {"house": house, "form": form}
                )

        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        house_id = kwargs.get("house_id", None)

        if house_id:
            house = get_object_or_404(House.objects.filter(id=house_id))
            if house.couple.homebuyer_set.filter(user=request.user).exists():
                house.delete()
                messages.success(request, "Your house has been deleted!")
                return redirect("home")

        return redirect("home")


class HouseAddView(BaseView):
    template_name = "core/houseAdd.html"

    def get(self, request, *args, **kwargs):
        house_form = HouseEditForm()
        return render(request, self.template_name, {"form": house_form})

    def post(self, request, *args, **kwargs):
        nickname = request.POST.get("nickname", None)
        address = request.POST.get("address", None)

        if nickname and address:
            couple = Couple.objects.filter(homebuyer__user=request.user).first()
            house = House.objects.create(
                nickname=nickname,
                address=address,
                couple=couple,
            )
            messages.success(request, "Your house has been added!")
            return redirect("eval", house_id=house.id)

        return redirect("house-add")


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
        homebuyer = Homebuyer.objects.get(user=request.user)

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
        homebuyer = Homebuyer.objects.get(user=request.user)
        house = get_object_or_404(House.objects.filter(id=kwargs["house_id"]))

        couple = Couple.objects.filter(homebuyer__user=request.user).first()
        categories = Category.objects.filter(homebuyer__user=request.user)

        for category in categories:
            id = category.id
            score = request.POST.get(str(category), 3)

            category = Category.objects.get(id=id)

            grade, created = Grade.objects.update_or_create(
                homebuyer=homebuyer,
                category=category,
                house=house,
                defaults={"score": int(score)},
            )

        messages.success(request, "Your evaluation has been saved!")

        return redirect("eval", house_id=house.id)


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
        homebuyer = Homebuyer.objects.get(user=request.user)
        couple = homebuyer.couple

        categories = Category.objects.filter(couple=couple)
        weights = CategoryWeight.objects.filter(homebuyer__user=request.user)

        weighted = {}
        for category in categories:
            missing = True
            for weight in weights:
                if weight.category.id == category.id:
                    weighted[category] = weight.weight
                    missing = False
                    break
            if missing:
                weighted[category] = 3

        eval_form = CategoryWeightForm(extra_fields=weighted, categories=categories)

        context = {
            "couple": couple,
            "weighted": weighted,
            "form": eval_form,
        }

        context.update(self._weight_context())

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        homebuyer = Homebuyer.objects.get(user=request.user)
        couple = homebuyer.couple

        categories = Category.objects.filter(couple=couple)

        for category in categories:
            id = category.id
            weight = request.POST.get(str(category), 3)

            category = Category.objects.get(id=id)

            category_weight, created = CategoryWeight.objects.get_or_create(
                homebuyer=homebuyer,
                category=category,
            )

            category_weight.weight = weight
            category_weight.save()

        messages.success(request, "Your category weights have been saved!")

        return redirect("categories")


class CategoryAddView(BaseView):
    template_name = "core/categoryAdd.html"

    def get(self, request, *args, **kwargs):
        form = CategoryAddForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        summary = request.POST.get("summary", None)
        description = request.POST.get("description", None)

        if summary and description:
            couple = Couple.objects.filter(homebuyer__user=request.user).first()
            category = Category.objects.create(
                summary=summary,
                description=description,
                couple=couple,
            )
            messages.success(request, "Your category has been added!")
            return redirect("categories")

        return redirect("categories")
