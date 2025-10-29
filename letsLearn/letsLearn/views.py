import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader
import math

from letsLearn.models import Product, Cart
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

            purchase_total = 1
            products_in_cart = Cart.objects.filter(user_id=1,product_id=product_id)

            if len(products_in_cart) > 0:
                purchase_total += products_in_cart[0].quantity
            if product.stock_qty - purchase_total >= 0:
                if len(products_in_cart) == 1:
                    products_in_cart[0].quantity += 1
                    products_in_cart[0].save()
                else:
                    products_in_cart = Cart(user_id=User.objects.get(id=1), product_id=Product.objects.get(id=product_id), quantity=1)
                    products_in_cart.save()
                    
                return JsonResponse({'status' : 'OK'})
            
            return JsonResponse({'error' : 'insufficient product amount'})
            
            
    return JsonResponse({'error' : 'Only POST requests are allowed'}, status = 405)

def shoppingcart(request):
    template = loader.get_template("cart.html")

    #p = Cart(user_id=User.objects.get(id=1), product_id=Product.objects.get(id=1), quantity=2)
    #p.save()
    #p = Cart(user_id=User.objects.get(id=1), product_id=Product.objects.get(id=20), quantity=1)
    #p.save()

    cart = Cart.objects.filter(user_id=1)
    total_price = 0
    prices = []

    for cart_item in cart:
        price = cart_item.product_id.price * cart_item.quantity

        total_price += price
        print("price: " + str(price) + "  total: " + str(total_price))
        prices.append(intToPrice(price))

    total_price = intToPrice(total_price)
    context =  {
        "cart": zip(cart, prices),
        "total_price": total_price,
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

    result = price[:(size - 2)] + "." + price[(size - 2):]

    return result
