#from django.http import HttpResponse
from django.shortcuts import render

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


######Product Page#######
def newListing(request):
    return render(request, 'newListing.html')

def productViewer(request):
    return render(request, 'productViewer.html')

