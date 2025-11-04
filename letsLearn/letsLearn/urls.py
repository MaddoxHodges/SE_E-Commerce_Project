"""
URL configuration for letsLearn project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from authapp import views as auth_views

urlpatterns = [
    #path ('', include('members.urls')),
    path('admin/', admin.site.urls),
    
    path('', views.homepage),
    
    path('about/', views.about),
     
    path('home/', views.homepage),

    path('marketplace/', views.marketplace),

    path('marketplace/details', views.details),

    path('addtocart', views.addtocart),

    path('cart/', views.shoppingcart),

    path('checkout/', views.checkout),

    path('placeorder/', views.placeorder),

    path('vieworders/', views.vieworders),

    path('vieworders/details', views.orderdetails),

    path('support/', views.support),

    path('login/', auth_views.login_view, name='login'),

    path('register/', auth_views.register_view, name='register'),

    path('logout/', auth_views.logout_view, name='logout'),

    path('productPage/', views.productPage),

    path('newListing/', views.newListing),

    path('productViewer/', views.productViewer),

    path('productEdit/', views.productEdit),

    path('tickets/', views.tickets),

    path('productReview/', views.productReview),

    path('newTicket/', views.newTicket),

    path('newTicket/', views.newTicket),

    path('buyerHome/', views.buyerHome),

    path('newAdmin/', views.newAdmin),
]




