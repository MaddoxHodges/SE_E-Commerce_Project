from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SellerProfile

User = get_user_model()

def register_view(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""
        confirm = request.POST.get("confirm") or ""
        is_seller = request.POST.get("is_seller") == "on"

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

        user = User.objects.create_user(username=email, email=email, password=password)
        
        SellerProfile.objects.create(
            user=user,
            is_seller=is_seller,          
            is_pending=is_seller,     
            is_approved=not is_seller,
            is_banned=False
        )

        if is_seller:
            messages.success(request, "Account created. Your seller request is pending admin approval.")
        else:
            messages.success(request, "Account created. Please sign in.")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""

        # Try to find user by email
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect("login")

        # Authenticate using username linked to that email
        user = authenticate(request, username=user_obj.username, password=password)

        if user is None:
            messages.error(request, "Invalid email or password.")
            return redirect("login")

        # Successful login
        login(request, user)

        sp = getattr(user, "sellerprofile", None)

        # Superuser/staff → admin support panel
        if user.is_superuser or user.is_staff:
            return redirect("/support/")

        # Banned?
        if sp and sp.is_banned:
            logout(request)
            messages.error(request, "Your account is banned.")
            return redirect("login")

        # Seller pending approval
        if sp and sp.is_seller and not sp.is_approved:
            logout(request)
            messages.info(request, "Your seller account request is still pending approval.")
            return redirect("login")

        # Approved seller
        if sp and sp.is_seller and sp.is_approved:
            return redirect("/productPage/")

        # Default buyer
        return redirect("/buyerHome/")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("/")


