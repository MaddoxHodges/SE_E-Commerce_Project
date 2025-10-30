import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template import loader
import math

from letsLearn.models import Product
from django.contrib.auth.models import User


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

def BuyerHome(request):
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

    # p = Product(title="Product 2", price=517, stock_qty=1, description="product 2 description")
    # p.save()
    # p = Product(title="Product 3", price=8, stock_qty=0, description="product 3 description")
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

def productPage(request):
    return render(request, 'productPage.html')

def support(request):
    return render(request, 'support.html')

def login(request):
    return render(request, 'login.html')
######Login Page#########
def createProfile(request):
    return render(request, 'createProfile.html')
def productEdit(request):
    return render(request, 'productEdit.html')


#######Admin Support#########
def tickets(request):
    return render(request, 'tickets.html')

def productReview(request):
    return render(request, 'productReview.html')

def NewTicket(request):
    return render(request, 'NewTicket.html')

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
    return render(request, 'buyerHome.html')

def productViewer(request):
    return render(request, 'productViewer.html')
