import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.contrib.auth import authenticate, login as auth_login
from .models import SupportTicket, TicketMessage
from authapp.models import SellerProfile
from django.contrib import messages

import math

from letsLearn.models import Product
from django.contrib.auth.models import User


######Homepage Links########
def homepage(request):
    #return HttpResponse("Hello World! I'm Home.")
    return render(request, 'home.html')


def productViewer(request):
    return render(request, 'productViewer.html')

def about(request):
    #return HttpResponse("My About page.")
    return render(request, 'about.html')

def buyerHome(request):
    return render(request, 'BuyerHome.html')


def marketplace(request):

    template = loader.get_template("marketplace.html")
    page = request.GET.get("page", 1)
    try:
        page = int(page)
    except ValueError as error:
        page = 1
    
    page = max(page, 1)
    ## pg_num = min(pg_num, 1)  waiting on db to check for max page number

    context =  {
        'next_page': page + 1,
        'prev_page': page - 1,
        'page': page,

    }

    # p = Product(title="Product 1", price=517, stock_qty=1, description="product 1 description")
    # p.save()
    # p = Product(title="Product 2", price=8, stock_qty=0, description="product 2 description")
    # p.save()

    # for i in range(20):
    #     p = Product(title=f"Product {i + 4}", price=100 + 20 * i, stock_qty=i, description=f"product {i} description")
    #     p.save()

    products = Product.objects.filter(is_approved=True)[(page - 1) * 12:(page * 12)]

    grid = []
    for row in range(math.ceil(len(products) / 3)):
        row_list = []
        for index in range(3):
            product_index = (row * 3) + index
            if len(products) <= product_index :
                break

            row_list.append(products[product_index])
        grid.append(row_list)
    
    context["grid"] = grid

    return HttpResponse(template.render(context, request))

def details(request):
    template = loader.get_template("details.html")
    product = Product.objects.get(id=request.GET.get("product_id"))
    context =  {
        "inStock": 1,
        "product": product,
        "price": intToPrice(product.price)
    }

    return HttpResponse(template.render(context, request))

def addtocart(request: HttpResponse):
    if request.method == 'POST':
            raw_body = request.body
            try:
                product_id = json.loads(raw_body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({'error' : 'Invalid JSON format'}, status = 400)
            
            product = Product.objects.get(id=product_id)

            cart = request.session.get("cart", {})
            # non string keys are converted into strings when passed into the cart, no idea why but it will not work unless you match it correctly 
            # (ex: getting the number 20 would attempt to get from an entirely new entry in the cookie labled as 20 while the actual data was being stored under the string "20")
            products_in_cart = cart.get(str(product_id), 0)
            purchase_total = 1 + products_in_cart

            if product.stock_qty - purchase_total >= 0:
                cart[str(product_id)] = purchase_total
                request.session["cart"] = cart

                return JsonResponse({'status' : 'OK'})
            
            return JsonResponse({'error' : 'insufficient product amount'})
            
            
    return JsonResponse({'error' : 'Only POST requests are allowed'}, status = 405)



def shoppingcart(request):
    template = loader.get_template("cart.html")

    cart = request.session.get("cart", {})
    total_price = 0
    product_data = []

    deletion_id = request.GET.get("product_id")
    if deletion_id in cart:
        cart[deletion_id] -= 1
        if cart[deletion_id] == 0:
            del cart[deletion_id]
        request.session["cart"] = cart
    for product_id in cart:
        # get the price of the item from the database and multiply it by the quanity in the cart cookie
        products = Product.objects.get(id=product_id)
        price = products.price * cart[product_id]

        total_price += price
        product_data.append({"quantity": cart[product_id], "title": products.title, "price": intToPrice(price), "product_id": product_id})

    total_price = intToPrice(total_price)
    context =  {
        "product_data": product_data,
        "total_price": total_price,
    }

    return HttpResponse(template.render(context, request))

def checkout(request):
    template = loader.get_template("checkout.html")

    cart = request.session.get("cart", {})
    total_price = 0
    product_data = []

    for product_id in cart:
        # get the price of the item from the database and multiply it by the quanity in the cart cookie
        products = Product.objects.get(id=product_id)
        if products.stock_qty < cart[product_id]:
            if (products.stock_qty == 0):
                del cart[product_id]
            else:
                cart[product_id] = products.stock_qty

        price = products.price * cart[product_id]

        total_price += price
        product_data.append({"quantity": cart[product_id], "title": products.title, "price": intToPrice(price), "product_id": product_id})

    request.session["cart"] = cart

    context =  {
        "product_data": product_data,
        "price": intToPrice(total_price),
        "tax": round(total_price/100 * .07, 2),
        "shipping": intToPrice(1700),
        "total": round(total_price/100 * 1.07 + 17, 2)

    }

    return HttpResponse(template.render(context, request))

def placeorder(request):
    template = loader.get_template("placeorder.html")

    cart = request.session.get("cart", {})
    total_price = 0

    for product_id in cart:
        product = Product.objects.get(id=product_id)
        if product.stock_qty < cart[product_id]:
            return redirect("/checkout")

    for product_id in cart:
        product = Product.objects.get(id=product_id)
        product.stock_qty -= cart[product_id]
        product.save()
    
    request.session["cart"] = {}

    context =  {
    }

    return HttpResponse(template.render(context, request))





######Login Page#########
def login(request):
    return render(request,"login.html")


########Admin Support#########

def productReview(request):
    if not request.user.is_staff:
        return redirect("/home")

    pending_sellers = SellerProfile.objects.filter(is_seller=True, is_approved=False)
    pending_products = Product.objects.filter(is_approved=False)

    return render(request, "productReview.html", {
        "pending_sellers": pending_sellers,
        "pending_products": pending_products
    })


def processModeration(request):
    if request.method != "POST":
        return redirect("productReview")

    # GET lists from POST form
    approved_sellers = request.POST.getlist("approve_seller")
    approved_products = request.POST.getlist("approve_product")

    # Approve Sellers
    for user_id in approved_sellers:
        try:
            profile = SellerProfile.objects.get(user__id=user_id)
            profile.is_seller = True
            profile.is_pending = False
            profile.is_approved = True
            profile.save()
        except SellerProfile.DoesNotExist:
            pass

    # Approve Products
    for product_id in approved_products:
        try:
            product = Product.objects.get(id=product_id)
            product.is_pending = False
            product.is_approved = True
            product.save()
        except Product.DoesNotExist:
            pass

    messages.success(request, "Approvals processed successfully.")
    return redirect("productReview")





def tickets(request):
    
    if not request.user.is_staff:
        return redirect("/home")

    tickets = SupportTicket.objects.all().order_by("-id")

    return render(request, "tickets.html", {
        "tickets": tickets,
        "role": "Admin"
    })

def closeTicket(request, ticket_id):
    if not request.user.is_staff:
        return redirect("/newTicket/")  

    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
    except SupportTicket.DoesNotExist:
        return redirect("/tickets/")

    ticket.status = "Closed"
    ticket.save()

    return redirect(f"/replyTicket/{ticket_id}/")


def replyTicket(request, ticket_id):
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
    except SupportTicket.DoesNotExist:
        return redirect("/newTicket/")

    
    if request.method == "POST" and ticket.status != "Closed":
    
        msg = request.POST.get("message") or request.POST.get("response") or ""
        msg = msg.strip()

        
        if msg == "":
            from django.contrib import messages
            messages.error(request, "Message cannot be empty.")
            return redirect(f"/replyTicket/{ticket_id}/")

        TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=msg
        )

        
        if request.user.is_staff:
            ticket.status = "Pending User"
        else:
            ticket.status = "Pending Admin"

        ticket.save()
        return redirect(f"/replyTicket/{ticket_id}/")

    
    ticket_messages = ticket.messages.order_by("timestamp")

    return render(request, "replyTicket.html", {
        "ticket": ticket,
        "messages": ticket_messages
    })




def support(request):
    
    return render(request, 'support.html')

def newAdmin(request):
    admin_created = False
    error = ""

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if User.objects.filter(username=email).exists():
            error = "Admin with this email already exists"
        
        elif password != confirm:
            error = "Passwords do not match"

        elif len(password) < 8:
            error = "Password must be at least 8 characters"

        else:
            User.objects.create_user(
                username=email,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=True
            )
            admin_created = True

    return render(request, 'newAdmin.html', {"admin_created": admin_created, "error": error})

########Seller Pages##########
def productViewer(request):
    if not request.user.is_authenticated:
        return redirect("login")

    products = Product.objects.filter(seller=request.user, is_approved=True).order_by("-id")

    return render(request, 'productViewer.html', {"products": products})


def productEdit(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id") 

        product = Product.objects.get(id=product_id)

        # verify seller owns product
        if request.user != product.seller:
            return redirect("/home")

        
        product.title = request.POST.get("title")
        product.description = request.POST.get("description")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.save()

        return redirect("/productPage")

    else:
        # If GET, show the edit page
        product_id = request.GET.get("product_id")
        product = Product.objects.get(id=product_id)

        return render(request, "productedit.html", {"product": product})


def productPage(request):
    return render(request, 'productPage.html')


def newTicket(request):
    
    user = request.user

    if user.is_superuser or user.is_staff:
        role = "Admin"
    elif hasattr(user, "sellerprofile") and user.sellerprofile.is_seller:
        role = "Seller"
    else:
        role = "Buyer"
    if request.method == "POST":
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        SupportTicket.objects.create(
            user=user,
            subject=subject,
            description=message,
            status="Open"
        )

        if role == "Seller":
            return redirect("/productPage/")
        else:
            return redirect("/buyerHome/")

    # Load user's tickets
    tickets = SupportTicket.objects.filter(user=user).order_by("-id")

    return render(request, "newTicket.html", {"tickets": tickets, "role": role})



def intToPrice(price):
    price = str(price)
    size = len(price)
    while size < 3:
        price = "0" + price
        size = len(price)

    result = price[:(size - 2)] + "." + price[(size - 2):]
    return result


def buyerHome(request):
    return render(request, 'buyerHome.html')

def newListing(request):

    if request.method == "POST":
        title = request.POST.get("productName")
        desc = request.POST.get("productDes")
        price = request.POST.get("productPrice")

        price_value = float(price)

        Product.objects.create(
            title=title,
            description=desc,
            price=price_value,
            stock=1,                  
            seller=request.user,
            is_approved=False  
        )

        return redirect("/productPage/")

    return render(request, 'newListing.html')




def replyUser(request, ticket_id):
    # Safe ticket lookup
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
    except SupportTicket.DoesNotExist:
        return redirect("/newTicket/")

    # Only ticket owner can reply
    if ticket.user != request.user:
        return HttpResponse("Unauthorized", status=403)

    # No replies if ticket is closed
    if ticket.status == "Closed":
        return redirect("/newTicket/")

    # Handle reply form
    if request.method == "POST":
        user_message = request.POST.get("message")

        # Create reply
        TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=user_message
        )

        # Update status so admin knows they need to respond
        ticket.status = "Pending Admin"
        ticket.save()

        return redirect(f"/replyTicket/{ticket_id}/")

    return redirect(f"/replyTicket/{ticket_id}/")

def webUsers(request):
    if not request.user.is_staff:
        return redirect("/home")

    users = User.objects.all()
    user_data = []

    for u in users:
        profile = getattr(u, "sellerprofile", None)
        role = "Seller" if profile and profile.is_seller else "Buyer"
        is_banned = profile.is_banned if profile else False
        
        user_data.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": role,
            "is_banned": is_banned
        })

    return render(request, "webUsers.html", {"users": user_data})

def banUser(request, user_id):
    if request.method == "POST":
        user = User.objects.get(id=user_id)
        
        # Prevent admin ban
        if user.is_superuser:
            messages.error(request, "Admins cannot be banned.")
            return redirect("webUsers")

        profile, _ = SellerProfile.objects.get_or_create(user=user)
        profile.is_banned = True
        profile.save()

        # Refresh so UI reflects instantly
        profile.refresh_from_db()

        messages.success(request, f"{user.username} has been banned.")
    return redirect("webUsers")


def unbanUser(request, user_id):
    if request.method == "POST":
        user = User.objects.get(id=user_id)
        profile, _ = SellerProfile.objects.get_or_create(user=user)
        profile.is_banned = False
        profile.save()
        profile.refresh_from_db()

        messages.success(request, f"{user.username} has been unbanned.")
    return redirect("webUsers")