# Import json
import json


# Django imports
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render


# App imports
from .forms import CategoryDeleteForm
from .forms import CategoryEditForm
from .forms import CategoryWeightEditForm
from .models import Category
from .models import CategoryWeight
from realestate.apps.appauth.models import User
from realestate.apps.core.models import Couple
from realestate.apps.core.models import Homebuyer
from realestate.apps.core.views import BaseView


# Class based view to display the categories
class CategoryListView(BaseView):
    # Get the allowed user types
    _USER_TYPES_ALLOWED = User._HOMEBUYER_ONLY

    # Set the template name
    template_name = "categories/list_category.html"

    # Set the form class
    form_class = CategoryWeightEditForm

    # Method to check the permissions
    def _permission_check(self, request, role, *args, **kwargs):
        return True

    # Method to get the weight context data
    def _weight_context(self):
        # Get the weight field
        weight_field = CategoryWeight._meta.get_field("weight")

        # Get the choices for the weight field
        weight_choices = dict(weight_field.choices)

        # Get the minimum and maximum weight
        min_weight = min(weight for weight in weight_choices)
        max_weight = max(weight for weight in weight_choices)

        # Set the minimum and maximum choices
        min_choice = weight_choices[min_weight]
        max_choice = weight_choices[max_weight]

        # Return the data
        return {
            "min_weight": min_weight,
            "max_weight": max_weight,
            "min_choice": min_choice,
            "max_choice": max_choice,
            "default_weight": weight_field.default,
            "js_weight": json.dumps(weight_choices),
        }

    # Method to handle the get request
    def get(self, request, *args, **kwargs):
        # Get the homebuyer and couple
        homebuyer = Homebuyer.objects.get(user=request.user)
        couple = homebuyer.couple

        # Get the categories and weights
        categories = Category.objects.filter(couple=couple)
        weights = CategoryWeight.objects.filter(homebuyer=homebuyer)

        # Map the categories to the weights
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

        # Populate the form
        form = self.form_class(extra_fields=weighted, categories=categories)

        # Set the hide button
        hide_button = False

        # If weights are not set
        if weighted == {}:
            # Hide the button
            hide_button = True

        # Set the context
        context = {
            "couple": couple,
            "weighted": weighted,
            "form": form,
            "hide_button": hide_button,
        }

        # Update the context
        context.update(self._weight_context())

        # Render the template
        return render(request, self.template_name, context)

    # Method to handle the post request
    def post(self, request, *args, **kwargs):
        # Get the homebuyer and couple
        homebuyer = Homebuyer.objects.get(user=request.user)
        couple = homebuyer.couple

        # Get the categories
        categories = Category.objects.filter(couple=couple)

        # Traverse the categories
        for category in categories:
            # Get the id and weight
            id = category.id
            weight = request.POST.get(str(category), 3)

            # Get the category for the id
            category = Category.objects.get(id=id)

            # Get or create the category weight
            category_weight, created = CategoryWeight.objects.get_or_create(
                homebuyer=homebuyer,
                category=category,
            )

            # Update the weight
            category_weight.weight = weight

            # Save the category weight
            category_weight.save()

        # Add a success message
        messages.success(request, "Your category weights have been saved!")

        # Redirect to the categories page
        return redirect("category-list")


# Class based view to add a category
class CategoryAddView(BaseView):
    # Set the template name
    template_name = "categories/add_category.html"

    # Set the form class
    form_class = CategoryEditForm

    def get(self, request, *args, **kwargs):
        # Initialize the form
        form = self.form_class()

        # Render the template
        return render(request, self.template_name, {"form": form})

    # Method to handle the post request
    def post(self, request, *args, **kwargs):
        # Get the summary and description from the post request
        summary = request.POST.get("summary", None)
        description = request.POST.get("description", None)

        # If the summary and description are not None
        if summary and description:
            # Get the couple
            couple = Couple.objects.filter(homebuyer__user=request.user).first()

            # Try to create the category
            try:
                # Create the category
                category = Category.objects.create(
                    summary=summary,
                    description=description,
                    couple=couple,
                )

            except:
                # Send an error message
                messages.error(request, "Your category could not be added!")

                # Redirect to the categories page
                return redirect("category-list")

            # Send a success message
            messages.success(request, "Your category has been added!")

            # Redirect to the categories page
            return redirect("category-list")

        # Send an error message
        messages.error(request, "Your category could not be added!")

        # Redirect to the categories page
        return redirect("category-list")


# Class based view to edit a category
class CategoryEditView(BaseView):
    # Set the template name
    template_name = "categories/edit_category.html"

    # Set the form class
    form_class = CategoryEditForm

    # Method to handle the get request
    def get(self, request, *args, **kwargs):
        # Get the category id
        category_id = kwargs.get("category_id", None)

        # If the category id is not None
        if category_id:
            # Get the category
            category = get_object_or_404(Category.objects.filter(id=category_id))

            # If the category is in the couple
            if category.couple.homebuyer_set.filter(user=request.user).exists():
                # Populate the form
                form = self.form_class(
                    initial={
                        "id": category.id,
                        "summary": category.summary,
                        "description": category.description,
                    }
                )

                # Render the template
                return render(
                    request,
                    self.template_name,
                    {"form": form, "category": category},
                )

        # Redirect to the categories page
        return redirect("category-list")

    # Method to handle the post request
    def post(self, request, *args, **kwargs):
        # Get the category id
        category_id = kwargs.get("category_id", None)

        # If the category id is not None
        if category_id:
            # Get the category
            category = get_object_or_404(Category.objects.filter(id=category_id))

            # If the category is in the couple
            if category.couple.homebuyer_set.filter(user=request.user).exists():
                # Populate the form
                form = self.form_class(request.POST)

                # If the form is valid
                if form.is_valid():
                    # Get the data from the form
                    category.summary = form.cleaned_data["summary"]
                    category.description = form.cleaned_data["description"]

                    # Save the category
                    category.save()

                    # Send a success message
                    messages.success(request, "Your category has been updated!")

                    # Redirect to the categories page
                    return redirect("category-list")

                # Send an error message
                messages.error(request, "Your category could not be updated!")

                # Render the template
                return render(
                    request,
                    self.template_name,
                    {"form": form, "category": category},
                )

        # Redirect to the categories page
        return redirect("category-list")


# Class based view to delete a category
class CategoryDeleteView(BaseView):
    # Set the template name
    template_name = "categories/delete_category.html"

    # Set the form class
    form_class = CategoryDeleteForm

    # Method to handle the get request
    def get(self, request, *args, **kwargs):
        # Get the category id
        category_id = kwargs.get("category_id", None)

        # If the category id is not None
        if category_id:
            # Get the category
            category = get_object_or_404(Category.objects.filter(id=category_id))

            # If the category is in the couple
            if category.couple.homebuyer_set.filter(user=request.user).exists():
                # Populate the form
                form = self.form_class(
                    initial={
                        "id": category.id,
                        "summary": category.summary,
                        "description": category.description,
                    }
                )

                # Render the template
                return render(
                    request, self.template_name, {"category": category, "form": form}
                )

        # Render the template
        return render(request, self.template_name, {})

    # Method to handle the post request
    def post(self, request, *args, **kwargs):
        # Get the category id
        category_id = kwargs.get("category_id", None)

        # If the category id is not None
        if category_id:
            # Get the category
            category = get_object_or_404(Category.objects.filter(id=category_id))

            # If the category is in the couple
            if category.couple.homebuyer_set.filter(user=request.user).exists():
                # Delete the category
                category.delete()

                # Send a success message
                messages.success(request, "Your category has been deleted!")

                # Redirect to the categories page
                return redirect("category-list")

        # Send an error message
        messages.error(request, "Your category could not be deleted!")

        # Redirect to the categories page
        return redirect("category-list")
