from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages

User = get_user_model()

def register_view(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""
        confirm = request.POST.get("confirm") or ""

        if not email or "@" not in email:
            messages.error(request, "Enter a valid email.")
            return redirect("register")
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return redirect("register")
        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("register")
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        User.objects.create_user(username=email, email=email, password=password)
        messages.success(request, "Account created. Please sign in.")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=email, password=password)
        if user is None:
            messages.error(request, "Invalid email or password.")
            return redirect("login")
        login(request, user)
        return redirect("/")
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("/")
