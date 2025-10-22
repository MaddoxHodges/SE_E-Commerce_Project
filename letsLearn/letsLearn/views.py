from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import ProductForm
from .models import Product


######Homepage Links########
def homepage(request):
    #return HttpResponse("Hello World! I'm Home.")
    return render(request, 'home.html')

def about(request):
    #return HttpResponse("My About page.")
    return render(request, 'about.html')

def marketplace(request):

    return render(request,'marketplace.html')

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
def productEdit(request):
    return render(request, 'productEdit.html')


######Product Page#######
def newListing(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
       

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            
        )

        return redirect('/productViewer/')
    
    return render(request, 'newListing.html')
def productViewer(request):
    products = Product.objects.all()
    return render(request, 'productViewer.html', {'products': products})
#######Admin Support#########
def tickets(request):
    return render(request, 'tickets.html')

def productReview(request):
    return render(request, 'productReview.html')

def NewTicket(request):
    return render(request, 'NewTicket.html')

