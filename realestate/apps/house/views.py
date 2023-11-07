import json
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from realestate.apps.core.views import BaseView
from realestate.apps.core.models import Homebuyer, Couple
from realestate.apps.categories.models import Category, Grade
from .models import House
from .forms import HouseEditForm, HouseDeleteForm, HouseEvalForm


class HouseEditView(BaseView):
    template_name = "house/edit_house.html"

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
    template_name = "house/delete_house.html"

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
    template_name = "house/add_house.html"

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


class HouseEvalView(BaseView):
    template_name = "house/eval_house.html"

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

        eval_form = HouseEvalForm(extra_fields=graded, categories=categories)
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
