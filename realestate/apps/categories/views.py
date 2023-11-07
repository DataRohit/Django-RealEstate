import json
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from realestate.apps.appauth.models import User
from realestate.apps.core.views import BaseView
from .models import Category, CategoryWeight
from .forms import CategoryEditForm, CategoryDeleteForm, CategoryWeightEditForm
from realestate.apps.core.models import Homebuyer, Couple


class CategoryListView(BaseView):
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

        eval_form = CategoryWeightEditForm(extra_fields=weighted, categories=categories)

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
    template_name = "categories/add_category.html"

    def get(self, request, *args, **kwargs):
        form = CategoryEditForm()
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


class CategoryEditView(BaseView):
    template_name = "categories/update_category.html"

    def get(self, request, *args, **kwargs):
        category_id = kwargs.get("category_id", None)

        if category_id:
            category = get_object_or_404(Category.objects.filter(id=category_id))
            if category.couple.homebuyer_set.filter(user=request.user).exists():
                house_form = CategoryEditForm(
                    initial={
                        "id": category.id,
                        "summary": category.summary,
                        "description": category.description,
                    }
                )

                return render(
                    request,
                    self.template_name,
                    {"form": house_form, "category": category},
                )

        return redirect("categories")

    def post(self, request, *args, **kwargs):
        category_id = kwargs.get("category_id", None)

        if category_id:
            category = get_object_or_404(Category.objects.filter(id=category_id))
            if category.couple.homebuyer_set.filter(user=request.user).exists():
                category_form = CategoryEditForm(request.POST)

                if category_form.is_valid():
                    category.summary = category_form.cleaned_data["summary"]
                    category.description = category_form.cleaned_data["description"]
                    category.save()

                    messages.success(request, "Your category has been updated!")

                    return redirect("categories")

                return render(
                    request,
                    self.template_name,
                    {"form": category_form, "category": category},
                )

        return redirect("categories")


class CategoryDeleteView(BaseView):
    template_name = "categories/delete_category.html"

    def get(self, request, *args, **kwargs):
        category_id = kwargs.get("category_id", None)

        if category_id:
            category = get_object_or_404(Category.objects.filter(id=category_id))
            if category.couple.homebuyer_set.filter(user=request.user).exists():
                form = CategoryDeleteForm(
                    initial={
                        "id": category.id,
                        "summary": category.summary,
                        "description": category.description,
                    }
                )
                return render(
                    request, self.template_name, {"category": category, "form": form}
                )

        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        category_id = kwargs.get("category_id", None)

        if category_id:
            category = get_object_or_404(Category.objects.filter(id=category_id))
            if category.couple.homebuyer_set.filter(user=request.user).exists():
                category.delete()
                messages.success(request, "Your category has been deleted!")
                return redirect("categories")

        return redirect("categories")
