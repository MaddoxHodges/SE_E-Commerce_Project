from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader
import math


######Homepage Links########
def homepage(request):
    #return HttpResponse("Hello World! I'm Home.")
    return render(request, 'home.html')

def about(request):
    #return HttpResponse("My About page.")
    return render(request, 'about.html')

def marketplace(request):

    template = loader.get_template("marketplace.html")
    pg_num = request.GET.get("page", 1)
    try:
        pg_num = int(pg_num)
    except ValueError as error:
        pg_num = 1
    
    pg_num = max(pg_num, 1)
    ## pg_num = min(pg_num, 1)  waiting on db to check for max page number

    context =  {
        "products": [
            {
                "title": "Product 1",
                "price": 1.10,
                "stock_qty": 3,
                "description": "Description of product.",
                "seller_id": 0,
                "product_id": 111
            },
            {
                "title": "Product 2",
                "price": 66.0,
                "stock_qty": 0,
                "description": "Different description of product.",
                "seller_id": 1,
                "product_id": 66
            },            
            {
                "title": "Product 3",
                "price": -20.28,
                "stock_qty": -10,
                "description": "Other, unique description of product.",
                "seller_id": 2,
                "product_id": 182
            },
                        {
                "title": "Product 1a",
                "price": 1.10,
                "stock_qty": 3,
                "description": "Description of product.",
                "seller_id": 0,
                "product_id": 111
            },
            {
                "title": "Product 2a",
                "price": 66.0,
                "stock_qty": 0,
                "description": "Different description of product.",
                "seller_id": 1,
                "product_id": 66
            },            
            {
                "title": "Product 3a",
                "price": -20.28,
                "stock_qty": -10,
                "description": "Other, unique description of product.",
                "seller_id": 2,
                "product_id": 182
            },
                        {
                "title": "Product 1b",
                "price": 1.10,
                "stock_qty": 3,
                "description": "Description of product.",
                "seller_id": 0,
                "product_id": 111
            },
            {
                "title": "Product 2b",
                "price": 66.0,
                "stock_qty": 0,
                "description": "Different description of product.",
                "seller_id": 1,
                "product_id": 66
            },            
            {
                "title": "Product 3b",
                "price": -20.28,
                "stock_qty": -10,
                "description": "Other, unique description of product.",
                "seller_id": 2,
                "product_id": 182
            },
                        {
                "title": "Product 1c",
                "price": 1.10,
                "stock_qty": 3,
                "description": "Description of product.",
                "seller_id": 0,
                "product_id": 111
            },
            {
                "title": "Product 2c",
                "price": 66.0,
                "stock_qty": 0,
                "description": "Different description of product.",
                "seller_id": 1,
                "product_id": 66
            },            
        ],
    }

    grid = []
    for row in range(math.ceil(len(context["products"]) / 3)):
        row_list = []
        for index in range(3):
            product_index = (row * 3) + index
            if len(context["products"]) <= product_index :
                break

            row_list.append(context["products"][product_index])
        grid.append(row_list)
    
    context["grid"] = grid

    return HttpResponse(template.render(context, request))

def details(request):
    template = loader.get_template("details.html")
    context =  {
        "product_id": request.GET.get("product_id"),

        "product":{
                "title": "Product 1",
                "price": 1.10,
                "stock_qty": 3,
                "description": "Description of product.",
                "seller_id": 0,
                "product_id": 111
            }
    }


    return HttpResponse(template.render(context, request))

def addtocart(request):
    return JsonResponse({'status': 'OK'})

def shoppingcart(request):
    return render(request, 'cart.html')

def productPage(request):
    return render(request, 'productPage.html')

def support(request):
    return render(request, 'support.html')

def login(request):
    return render(request, 'login.html')
######Login Page#########
def createProfile(request):
    return render(request, 'createProfile.html')


######Product Page#######
def newListing(request):
    return render(request, 'newListing.html')

def productViewer(request):
    return render(request, 'productViewer.html')

