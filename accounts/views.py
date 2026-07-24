from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


def signup(request):
    if request.method == "POST":

        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {
                "error": "Username already exists. Please choose another username."
            })

        # Create new user
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("login")

    return render(request, "signup.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(request, "login.html", {
            "error": "Invalid Username or Password"
        })

    return render(request, "login.html")


def user_logout(request):
    logout(request)
    return redirect("/")