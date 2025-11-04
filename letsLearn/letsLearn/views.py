import datetime
import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.contrib.auth import authenticate, login as auth_login
import math

from letsLearn.models import Product
from letsLearn.models import Orders
from letsLearn.models import OrderItems
from django.contrib.auth.models import User
from .forms import CheckoutForm


######Homepage Links########
def homepage(request):
    #return HttpResponse("Hello World! I'm Home.")
    return render(request, 'home.html')

def newListing(request):
    return render(request, 'newListing.html')

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
    #     p = Product(title=f"Product {i + 3}", price=100 + 20 * i, stock_qty=i, description=f"product {i + 3} description")
    #     p.save()

    products = Product.objects.all()[(page - 1) * 12:(page * 12)]

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
            print(json.loads(raw_body.decode('utf-8')))
            product_id, qty = json.loads(raw_body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error' : 'Invalid JSON format'}, status = 400)
        
        product = Product.objects.get(id=product_id)

        cart = request.session.get("cart", {})
        # non string keys are converted into strings when passed into the cart, no idea why but it will not work unless you match it correctly 
        # (ex: getting the number 20 would attempt to get from an entirely new entry in the cookie labled as 20 while the actual data was being stored under the string "20")
        products_in_cart = cart.get(str(product_id), 0)
        purchase_total = int(qty) + products_in_cart

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
        "form": CheckoutForm(),
        "product_data": product_data,
        "price": intToPrice(total_price),
        "tax": round(total_price/100 * .07, 2),
        "shipping": intToPrice(1700),
        "total": round(total_price/100 * 1.07 + 17, 2)

    }

    return HttpResponse(template.render(context, request))

def placeorder(request):
    template = loader.get_template("placeorder.html")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data["address"]
            cart = request.session.get("cart", {})
            total_price = 0

            for product_id in cart:
                product = Product.objects.get(id=product_id)
                if product.stock_qty < cart[product_id]:
                    return redirect("/checkout")

            order = Orders(created_at=datetime.datetime.now(), address=address, subtotal_cents=0, total_cents=0, tax_cents=0, shipping_cents=0)
            order.save()

            for product_id in cart:
                product = Product.objects.get(id=product_id)
                product.stock_qty -= cart[product_id]
                product.save()

                total_price += cart[product_id] * product.price
                order_item = OrderItems(order_id=order, product_id=product, price_cents=product.price, qty=cart[product_id], return_requested=False)
                order_item.save()
            
            order.subtotal_cents = total_price
            order.tax_cents = int(total_price * .07)
            order.shipping_cents = 1300
            order.total_cents = 1300 + int(total_price * 1.07)
            order.save()
            request.session["cart"] = {}

    context =  {
    }

    return HttpResponse(template.render(context, request))


def vieworders(request):

    template = loader.get_template("vieworders.html")
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

    # o = Orders(subtotal_cents=100, tax_cents=7, shipping_cents=1300, total_cents=1407, address="Test Address 1", created_at=datetime.datetime(2025, 10, 28, 12, 38, 0))
    # o.save()

    # o = Orders(subtotal_cents=1700, tax_cents=119, shipping_cents=1300, total_cents=3119, address="Test Address 1", created_at=datetime.datetime(2025, 11, 2, 9, 15, 0))
    # o.save()


    orders = Orders.objects.all()[(page - 1) * 12:(page * 12)]

    grid = []
    for row in range(math.ceil(len(orders) / 3)):
        row_list = []
        for index in range(3):
            product_index = (row * 3) + index
            if len(orders) <= product_index :
                break

            row_list.append(orders[product_index])
        grid.append(row_list)
    
    context["grid"] = grid

    return HttpResponse(template.render(context, request))

def orderdetails(request):
    template = loader.get_template("orderdetails.html")
    order = Orders.objects.get(id=request.GET.get("order_id"))

    return_id = request.GET.get("order_item_id")
    if return_id is not None:
        order_item = OrderItems.objects.get(id=return_id)
        if order_item:
            order_item.return_requested = True
            order_item.save()
    orderitems = []

    # o = OrderItems(order_id=order, product_id=Product.objects.get(id=12), qty=5, price_cents=20, return_requested=False)
    # o.save()
    

    for item in OrderItems.objects.filter(order_id=order.id):
        product = Product.objects.get(id=item.product_id.id)
        orderitems.append({"item": item, "product": product, "total": intToPrice(item.qty * item.price_cents)})

    prices = [intToPrice(order.subtotal_cents), intToPrice(order.tax_cents), intToPrice(order.shipping_cents), intToPrice(order.total_cents)]

    context =  {
        "order": order,
        "items": orderitems,
        "formated_prices": prices
    }

    return HttpResponse(template.render(context, request))


######Login Page#########
def login(request):
    return render(request,"login.html")


#######Admin Support#########
def tickets(request):
    return render(request, 'tickets.html')

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
def productReview(request):
    return render(request, 'productReview.html')

def productEdit(request):
    return render(request, 'productEdit.html')

def productPage(request):
    return render(request, 'productPage.html')

def newTicketSeller(request):
    return render(request, 'newTicketSeller.html')

def newTicket(request):
    return render(request, 'newTicket.html')



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
    return render(request, 'newListing.html')

def productViewer(request):
    return render(request, 'productViewer.html')



