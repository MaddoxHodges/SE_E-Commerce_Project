#from django.http import HttpResponse
from django.shortcuts import render
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

def support(request):
    return render(request, 'support.html')

