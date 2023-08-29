import re
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.shortcuts import redirect, render
from .forms import (ProfileUpdateForm, UserAuthenticationForm, UserForm, UserUpdateForm)


def user_signup(request):
    """
    Renders a signup form for both customers and merchants. 
    Handles form submissions, checks form validity, creates a new user account, 
    authenticates the user, logs in the user, and redirects them to the appropriate 
    page based on their user type. Displays error messages if the form is invalid.
    """
    error_list = []

    if request.method == "POST":
        form = UserForm(request.POST)

        # Store errors to displays if form is invalid
        error_list = re.sub(r'\*\s*(password2|email)\n', '', form.errors.as_text())
        error_list = list(re.sub(r'\*.*?', '', error_list).split("\n"))

        if form.is_valid():
            form.save()
            messages.success(request, f"Account created successfully")
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            login(request, user)
            messages.success(request, f"Welcome {user.name}")
            if form.cleaned_data['user_type'] == "Merchant":
                return redirect("/store/dashboard")
            else:
                return redirect("/")
        else:
            messages.error(request, "Invalid information!")
    
    # Render signup form if request method is not POST
    form = UserForm()
    context = {'show_navbar_footer': True, "signup_form": form, "error_list": error_list}
    return render(request, 'account/signup.html', context)


def user_login(request):
    """
    Renders a login form and handles form submissions. Checks the validity of 
    the submitted form and authenticates the user. If authentication is successful,
    logs in the user, displays a welcome message, and redirects the user to 
    the appropriate page based on their user type. Displays error messages if the 
    form is invalid or if authentication fails.
    """
    if request.method == "POST":
        form = UserAuthenticationForm(request.POST)

        if form.is_valid():
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome {user.name}")
                if user.user_type == "Merchant":
                    return redirect("/store/dashboard/")
                else:
                    return redirect("/")
            else:
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Invalid email or password")

    # Render login form if request method is not POST
    form = UserAuthenticationForm()
    context = {'show_navbar_footer': True, "login_form": form}
    return render(request, 'account/login.html', context)


@login_required
def user_logout(request):
    """
    Logs out the authenticated user and redirects them to the homepage.
    """
    logout(request)
    messages.success(request, "You have successfully logged out")
    return redirect("/")


@login_required
def user_profile(request):
    """
    Renders the user's profile page with their profile data.
    """
    # Convert user's profile object to dictionary
    user_data = model_to_dict(request.user.profile)

    context = {'show_navbar_footer': True, "user_data": user_data}
    return render(request, 'account/profile.html', context)


@login_required
def update_profile(request):
    """
    Renders the profile update page and handles the submission of the profile update form.
    """
    
    if request.method == "POST":
        # Create user update and profile update forms with POST data and files
        u_form = UserUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
        p_form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user.profile)
        
        # If both forms are valid, save the updated user and profile data and redirect to the profile page
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Profile details updated successfully")
            return redirect("/store/profile/")
    else:
        # Create user update and profile update forms with current user data
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context =  {'show_navbar_footer': True, "user_update_form": u_form, "profile_update_form": p_form}
    return render(request, 'account/update_profile.html', context)