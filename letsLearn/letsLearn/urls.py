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
from django.conf import settings
from django.conf.urls.static import static


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

    path('productEdit/', views.productEdit, name='productEdit'),

    path('tickets/', views.tickets),

    path('productReview/', views.productReview),

    path('newTicket/', views.newTicket),

    path('newTicket/', views.newTicket),

    path('buyerHome/', views.buyerHome),

    path('newAdmin/', views.newAdmin),
    
    path("replyTicket/<int:ticket_id>/", views.replyTicket, name="replyTicket"),
    
    path("closeTicket/<int:ticket_id>/", views.closeTicket, name="closeTicket"),

    path("sellerOrders/", views.sellerOrders, name="sellerOrders"),
    
    path("sellerPayout/", views.sellerPayout, name="sellerPayout"),
    
    path("order/<int:order_id>/", views.orderdetails, name="orderDetails"),

    ##banning actions##
    path('webUsers/', views.webUsers, name='webUsers'),
    path('banUser/<int:user_id>/', views.banUser, name='banUser'),
    path('unbanUser/<int:user_id>/', views.unbanUser, name='unbanUser'),

    ###Admin Reviews###
   
    path("productReview/", views.productReview, name="productReview"),
    path("productReview/process/", views.processModeration, name="processModeration"),

    path("searchProducts/", views.searchProducts),

    path("details/", views.details, name="details"),

    path("requestRefund/<int:order_id>/", views.requestRefund, name="requestRefund"),
    path("acceptRefund/<int:order_id>/", views.acceptRefund, name="acceptRefund"),

    path("acceptRefund/<int:ticket_id>/", views.acceptRefund, name="acceptRefund"),
    path("denyRefund/<int:ticket_id>/", views.denyRefund, name="denyRefund"),

    path("tags/", views.Tags, name="tags"),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
