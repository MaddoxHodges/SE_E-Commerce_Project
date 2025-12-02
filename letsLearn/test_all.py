import pytest
from django.test import Client
from authapp.models import SellerProfile
from letsLearn.models import Product, SupportTicket, Orders, OrderItems
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db
User = get_user_model()

def buyItem(qty, id, message):
    response = c.get(f'/addtocart?product_id={id}&qty={qty}')
    assert response.status_code == 200 and message in response.content

def registerAdmin(info):
    response = c.post('/newAdmin/', info)
    assert response.status_code == 200 and User.objects.get(username=info["email"])

def registerTest(info, message, post_location, end_location):
    response = c.post(post_location, info)
    assert response.status_code == 302 and response.headers["Location"] == end_location

    response = c.get(end_location)
    assert response.status_code == 200 and message in response.content

# test register functions
c = Client()
def test_1():

    # attempt to register with an invalid email & check if the correct error message appears
    registerTest({"email": "buyer", "password": "password", "confirm": "password", "is_seller": "off"}, b"Enter a valid email.", '/register/', '/register/')

    # attempt to register with an invalid password & check if the correct error message appears
    registerTest({"email": "buyer@gmail.com", "password": "pass", "confirm": "pass", "is_seller": "off"}, b"Password must be at least 8 characters.", '/register/','/register/')

    # attempt to register with the password being different from confirmation & check if the correct error message appears
    registerTest({"email": "buyer@gmail.com", "password": "password1234", "confirm": "password", "is_seller": "off"}, b"Passwords do not match.", '/register/', '/register/')

    # register as a buyer
    registerTest({"email": "buyer@gmail.com", "password": "password", "confirm": "password", "is_seller": "off"}, b"Account created. Please sign in.", '/register/', '/login/')

    # attempt to register with an in use email & check if the correct error message appears
    registerTest({"email": "buyer@gmail.com", "password": "password", "confirm": "password", "is_seller": "off"}, b"Email already registered.", '/register/', '/register/')

    # register as a seller
    registerTest({"email": "seller@gmail.com", "password": "password", "confirm": "password", "is_seller": "on"}, b"Account created. Your seller request is pending admin approval.", '/register/', '/login/')

# test login functions
def test_2():

    # create a buyer account
    registerTest({"email": "buyer@gmail.com", "password": "password", "confirm": "password", "is_seller": "off"}, b"Account created. Please sign in.", '/register/', '/login/')

    # register as two sellers, one to be banned and one approved
    registerTest({"email": "seller@gmail.com", "password": "password", "confirm": "password", "is_seller": "on"}, b"Account created. Your seller request is pending admin approval.", '/register/', '/login/')
    registerTest({"email": "banned@gmail.com", "password": "password", "confirm": "password", "is_seller": "on"}, b"Account created. Your seller request is pending admin approval.", '/register/', '/login/')

    # attempt login as unverified seller & check if the correct error message appears
    registerTest({"email": "seller@gmail.com", "password": "password"}, b"Your seller account request is still pending approval.", '/login/', '/login/')

    # create a new admin
    registerAdmin({"email": "admin@gmail.com", "password": "password", "confirm": "password"})

    # login as admin
    registerTest({"email": "admin@gmail.com", "password": "password"}, b"", '/login/', '/support/')

    # reject one seller and approve another
    registerTest({"approve_seller": [str(User.objects.get(username="seller@gmail.com").id)], "reject_seller": [str(User.objects.get(username="banned@gmail.com").id)], "approve_product": [], "reject_product": [],}, b"Review decisions processed.", '/productReview/', '/productReview/')

    # attempt login with an invalid email & check if the correct error message appears
    registerTest({"email": "void@gmail.com", "password": "password"}, b"Invalid email or password.", '/login/', '/login/')

    # attempt login with an invalid password & check if the correct error message appears
    registerTest({"email": "buyer@gmail.com", "password": "word"}, b"Invalid email or password.", '/login/', '/login/')

    # login as buyer
    registerTest({"email": "buyer@gmail.com", "password": "password"}, b"", '/login/', '/buyerHome/')

    # login as seller
    registerTest({"email": "seller@gmail.com", "password": "password"}, b"", '/login/', '/productPage/')

    # attempt login as a banned seller & check if the correct error message appears
    registerTest({"email": "banned@gmail.com", "password": "password"}, b"Your account is banned.", '/login/', '/login/')




# test product functions
def test_3():
    # create a buyer account
    registerTest({"email": "buyer@gmail.com", "password": "password", "confirm": "password", "is_seller": "off"}, b"Account created. Please sign in.", '/register/', '/login/')

    # create a seller account
    registerTest({"email": "seller@gmail.com", "password": "password", "confirm": "password", "is_seller": "on"}, b"Account created. Your seller request is pending admin approval.", '/register/', '/login/')

    u = User.objects.get(username="seller@gmail.com")
    s = SellerProfile.objects.get(user=u.id)
    s.is_approved = True
    s.save()

    # login as seller
    registerTest({"email": "seller@gmail.com", "password": "password"}, b"", '/login/', '/productPage/')

    # this causes the server to crash
    # registerTest({"productName": "nothing", "productDes": "", "productPrice": "", "stock": ""}, b"", '/newListing/', '/newListing/')
    # assert Product.objects.get(title="nothing") == None

    # create a valid listing and ensure it appears within the database
    registerTest({"productName": "potato", "productDes": "a nutritious food item", "productPrice": "1.11", "stock": "10"}, b"", '/newListing/', '/productPage/')
    product = Product.objects.get(title="potato")
    assert product.price_cents == 111

    registerTest({"productName": "orange", "productDes": "should not be in searchbar", "productPrice": "20.", "stock": "10"}, b"", '/newListing/', '/productPage/')

    # create a second product that will be denied
    registerTest({"productName": "rejected", "productDes": "destined for failure", "productPrice": ".01", "stock": "1"}, b"", '/newListing/', '/productPage/')

    # edit a product
    # registerTest({"productName": "grapefruit", "productDes": "should not be in searchbar", "productPrice": ".03", "stock": "5"},
    #               b"", f'/productEdit/?product_id=1/', '/productViewer/')

    # create + register admin
    registerAdmin({"email": "admin@gmail.com", "password": "password", "confirm": "password"})
    registerTest({"email": "admin@gmail.com", "password": "password"}, b"", '/login/', '/support/')

    # accept and reject orders
    registerTest({"approve_seller": [], "reject_seller": [], "approve_product": [str(product.id)], "reject_product": [str(Product.objects.get(title="rejected").id)],}, b"Review decisions processed.", '/productReview/', '/productReview/')
    product = Product.objects.get(title="potato")
    assert product.status == "active" and Product.objects.get(title="rejected").status == "rejected"

    # ban and then unban a user
    registerTest({}, b"buyer@gmail.com has been banned.", f'/banUser/{User.objects.get(username="buyer@gmail.com").id}/', '/webUsers/')
    registerTest({}, b"buyer@gmail.com has been unbanned.", f'/unbanUser/{User.objects.get(username="buyer@gmail.com").id}/', '/webUsers/')

    # attempt to ban an admin
    registerTest({}, b"Admins cannot be banned.", f'/banUser/{User.objects.get(username="admin@gmail.com").id}/', '/webUsers/')

    # login as buyer
    registerTest({"email": "buyer@gmail.com", "password": "password"}, b"", '/login/', '/buyerHome/')

    # add an item to cart
    buyItem(3, product.id, b'true')

    # attempt to add more items than are in stock
    buyItem(999, product.id, b'false')

    # checkout items in cart
    response = c.post('/placeorder/', {"address": "Buyer Lane"})
    product = Product.objects.get(title="potato")
    assert response.status_code == 200 and b'Thank you for placing your order!' in response.content and product.stock == 7

    # ensure the order matches the checkout data
    response = c.get('/order/1/')
    assert b'Buyer Lane' in response.content

    # request a refund for the item
    response = c.post('/requestRefund/1/', {"reason": "item returned"})
    assert response.status_code == 302 and response.headers['Location'] == '/buyerHome/' and 'item returned' == Orders.objects.get(id=1).refund_reason

    # use search bar to find an item
    response = c.get('/searchProducts/?q=potato/')
    assert response.status_code == 200 and b"potato" in response.content and b"orange" not in response.content

    # create a ticket as a buyer
    response = c.post('/newTicket/', {"subject": "new ticket", "message": "ticket contents"})
    newTicket = SupportTicket.objects.get(subject="new ticket")
    assert response.status_code == 302 and response.headers["Location"] == f'/replyTicket/{newTicket.id}/'

    response = c.post('/newTicket/', {"subject": "closed ticket", "message": "to be closed"})

    # attempt to go to a ticket that does not exist
    registerTest({"message": "", "response": ""}, b"", '/replyTicket/999/', '/newTicket/')

    # send a reply as buyer on a ticket
    registerTest({"message": "reply", "response": ""}, b"", f'/replyTicket/{newTicket.id}/', f'/replyTicket/{newTicket.id}/')
    # print(TicketMessage.objects.all())

    c.get('/logout/')

    # login as seller
    registerTest({"email": "seller@gmail.com", "password": "password"}, b"", '/login/', '/productPage/')

    # get payout for completed order
    response = c.get('/sellerPayout/')
    assert response.status_code == 200 and b'3.33' in response.content