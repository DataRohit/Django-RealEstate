# Import json
import json


# Django imports
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render


# App imports
from .forms import HouseDeleteForm
from .forms import HouseEditForm
from .forms import HouseEvalForm
from .models import House
from realestate.apps.appauth.models import User
from realestate.apps.categories.models import Category
from realestate.apps.categories.models import Grade
from realestate.apps.core.models import Couple
from realestate.apps.core.models import Homebuyer
from realestate.apps.core.views import BaseView


# Class based view to handle the house edit
class HouseEditView(BaseView):
    # Set the template name
    template_name = "house/edit_house.html"

    # Set the form class
    form_class = HouseEditForm

    # Method to get the house
    def get(self, request, *args, **kwargs):
        # Get the house id
        house_id = kwargs.get("house_id", None)

        # If the house id exists
        if house_id:
            # Get the houes for the house id
            house = get_object_or_404(House.objects.filter(id=house_id))

            # If the house exist
            if house.couple.homebuyer_set.filter(user=request.user).exists():
                # Populate the form with the house data
                form = self.form_class(
                    initial={"nickname": house.nickname, "address": house.address}
                )

                # Render the template
                return render(
                    request, self.template_name, {"form": form, "house": house}
                )

        # Redirect to the home page
        return redirect("home")

    # Method to post the form
    def post(self, request, *args, **kwargs):
        # Get the house id
        house_id = kwargs.get("house_id", None)

        # If the house id exists
        if house_id:
            # Get the house for the house id
            house = get_object_or_404(House.objects.filter(id=house_id))

            # If the house exist
            if house.couple.homebuyer_set.filter(user=request.user).exists():
                # Populate the form with the house data
                form = self.form_class(request.POST)

                # If the form is valid
                if form.is_valid():
                    # Get the cleaned data
                    house.nickname = form.cleaned_data["nickname"]
                    house.address = form.cleaned_data["address"]

                    # Check if the nickname already exists
                    exists = (
                        House.objects.filter(nickname=house.nickname)
                        .exclude(id=house.id)
                        .exists()
                    )

                    # If the nickname already exists
                    if exists:
                        # Send a error message
                        error = (
                            f"House with nickname '{house.nickname}' already exists!"
                        )
                        messages.error(request, error)

                        # Redirect to the house edit page
                        return redirect("house-edit", house_id=house.id)

                    # Save the house
                    house.save()

                    # Add a success message
                    messages.success(request, "Your house has been updated!")

                    # Redirect to the house edit page
                    return redirect("house-edit", house_id=house.id)

                # Send a message that the form is invalid
                messages.error(request, "Your form is invalid!")

                # Render the template
                return render(
                    request, self.template_name, {"form": form, "house": house}
                )

        # Redirect to the home page
        return redirect("home")


# Class based view to handle the house delete
class HouseDeleteView(BaseView):
    # Set the template name
    template_name = "house/delete_house.html"

    # Set the form class
    form_class = HouseDeleteForm

    # Method to handle the get request
    def get(self, request, *args, **kwargs):
        # Get the house id
        house_id = kwargs.get("house_id", None)

        # If the house id exists
        if house_id:
            # Get the house
            house = get_object_or_404(House.objects.filter(id=house_id))

            # If the house exist
            if house.couple.homebuyer_set.filter(user=request.user).exists():
                # Populate the form with the house data
                form = self.form_class(
                    initial={"nickname": house.nickname, "address": house.address}
                )

                # Render the template
                return render(
                    request, self.template_name, {"house": house, "form": form}
                )

        # Render empty template
        return render(request, self.template_name, {})

    # Method to handle the post request
    def post(self, request, *args, **kwargs):
        # Method to handle the post request
        house_id = kwargs.get("house_id", None)

        # If the house id exists
        if house_id:
            # Get the house for the house id
            house = get_object_or_404(House.objects.filter(id=house_id))

            # If the house exist
            if house.couple.homebuyer_set.filter(user=request.user).exists():
                # Delete the house
                house.delete()

                # Send a success message
                messages.success(request, "Your house has been deleted!")

                # Redirect to the home page
                return redirect("home")

        # Send an error message
        messages.error(request, "Your house could not be deleted!")

        # Redirect to the home page
        return redirect("home")


# Method to handle the house add
class HouseAddView(BaseView):
    # Set the template name
    template_name = "house/add_house.html"

    # Set the form class
    form_class = HouseEditForm

    # Method to handle the get request
    def get(self, request, *args, **kwargs):
        # Initialize the form
        form = self.form_class()

        # Render the template
        return render(request, self.template_name, {"form": form})

    # Method to handle the post request
    def post(self, request, *args, **kwargs):
        # Get the form data
        nickname = request.POST.get("nickname", None)
        address = request.POST.get("address", None)

        # If the nickname and address exists
        if nickname and address:
            # Get the couple for the user
            couple = Couple.objects.filter(homebuyer__user=request.user).first()

            # Check if the nickname already exists
            exists = House.objects.filter(couple=couple, nickname=nickname).exists()

            # If the nickname already exists
            if exists:
                # Send a error message
                error = f"House with nickname '{nickname}' already exists!"
                messages.error(request, error)

                # Redirect to the house add page
                return redirect("house-add")

            # Create the house for the couple
            house = House.objects.create(
                nickname=nickname,
                address=address,
                couple=couple,
            )

            # Send a success message
            messages.success(request, "Your house has been added!")

            # Redirect to the house edit page
            return redirect("house-eval", house_id=house.id)

        # Send a error message
        messages.error(request, "Your house could not be added!")

        # Redirect to the house add page
        return redirect("house-add")


# Method to handle the house evaluation
class HouseEvalView(BaseView):
    # Set the template name
    template_name = "house/eval_house.html"

    # Set the form class
    form_class = HouseEvalForm

    # Method to check the permission
    def _permission_check(self, request, role, *args, **kwargs):
        # If user is homebuyer
        if role.role_type in User._HOMEBUYER_ONLY:
            # Get the house id
            house_id = kwargs.get("house_id", None)

            # If the couple exists
            if role.couple.house_set.filter(id=house_id).exists():
                # Permission granted
                return True

        # Permission denied
        return False

    # Method to update the score context
    def _score_context(self):
        # Get the score field
        score_field = Grade._meta.get_field("score")

        # Get the choices for the score field
        score_choices = dict(score_field.choices)

        # Get the min and max score
        min_score = min(score for score in score_choices)
        max_score = max(score for score in score_choices)

        # Set the min and max choice
        min_choice = score_choices[min_score]
        max_choice = score_choices[max_score]

        # Return the context
        return {
            "min_score": min_score,
            "max_score": max_score,
            "min_choice": min_choice,
            "max_choice": max_choice,
            "default_score": score_field.default,
            "js_scores": json.dumps(score_choices),
        }

    # Method to handle the get request
    def get(self, request, *args, **kwargs):
        # Get the homebuyer for the user
        homebuyer = Homebuyer.objects.get(user=request.user)

        # Get the house for the house id
        house = get_object_or_404(House, id=kwargs["house_id"])

        # Get the couple for the user
        couple = homebuyer.couple

        # Get the categories for the couple
        categories = Category.objects.filter(couple__id=couple.id)

        # Filter the grades for the house and user
        grades = Grade.objects.filter(house=house, homebuyer=homebuyer)

        # Map the categories to the grades
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

        # Populate the form
        eval_form = self.form_class(extra_fields=graded, categories=categories)

        # Prepare the context
        context = {
            "couple": couple,
            "house": house,
            "graded": graded,
            "form": eval_form,
        }

        # Update the context with the score context
        context.update(self._score_context())

        # Render the template
        return render(request, self.template_name, context)

    # Method to handle the post request
    def post(self, request, *args, **kwargs):
        # Get the homebuyer for the user
        homebuyer = Homebuyer.objects.get(user=request.user)

        # Get the couple for the user
        couple = homebuyer.couple

        # Get the house for the house id
        house = get_object_or_404(House, id=kwargs["house_id"])

        # Get the cateogries for the couple
        categories = Category.objects.filter(couple=couple)

        # Traverse the categories
        for category in categories:
            # Get the id and score for the category
            id = category.id
            score = request.POST.get(str(category), 3)

            # Get the category for the id
            category = Category.objects.get(id=id)

            # Update/Create the grade
            grade, created = Grade.objects.update_or_create(
                homebuyer=homebuyer,
                category=category,
                house=house,
                defaults={"score": int(score)},
            )

        # Send a success message
        messages.success(request, "Your evaluation has been saved!")

        # Redirect to the house evaluation page
        return redirect("house-eval", house_id=house.id)
