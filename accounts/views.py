from django.shortcuts import render, redirect
from .forms import RegistrationForm,LoginForm
from django.contrib.auth import login

# Create your views here.

def register_view(request):
    form = RegistrationForm()

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
           new_user=form.save()

           login(request, new_user )
           return redirect("accounts:register")



    context = {
        "form": form
    }
    return render(request, "accounts/register.html", context)



def login_view(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)
            return redirect("accounts:login")

    context = {
        "form": form
    }
    return render(request, "accounts/login.html", context)