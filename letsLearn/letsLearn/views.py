import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.contrib.auth import authenticate, login as auth_login
from datetime import datetime
from django.db.models import Q
import math

from letsLearn.models import Product
from django.contrib.auth.models import User


######Homepage Links########
def homepage(request):
    #return HttpResponse("Hello World! I'm Home.")
    return render(request, 'home.html')

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
    if request.method == 'POST':
        id = request.POST.get('id') or None
        seller_id = request.POST.get('seller_id') or None
        category_id = request.POST.get('category_id') or None
        title = request.POST.get('title') or None
        description = request.POST.get('description') or None
        price_cents = request.POST.get('price_cents') or None
        status = request.POST.get('status') or None
        main_image_url = request.POST.get('main_image_url') or None
        created_at = request.POST.get('created_at') or None
        updated_at = request.POST.get('updated_at') or None

        if not created_at:
            created_at = datetime.now()
        if not updated_at:
            updated_at = datetime.now()

        Product.objects.create(
            id=id,
            seller_id=seller_id,
            category_id=category_id,
            title=title,
            description=description,
            price_cents=price_cents,
            status=status,
            main_image_url=main_image_url,
            created_at=created_at,
            updated_at=updated_at,
        )

        return redirect('/productViewer/')
    return render(request, 'newListing.html')


def productViewer(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'productViewer.html', context)
def searchProducts(request):
    query = request.GET.get('q', '').strip()
    products = []

    if query:
    
        products = Product.objects.filter(title__icontains=query)

        if not products.exists():
            products = Product.objects.filter(description__icontains=query)
    else:
        products = Product.objects.all()

    context = {
        'products': products,
        'query': query,
        'search_performed': bool(query),
    }
    return render(request, 'searchProducts.html', context)
