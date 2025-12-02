import datetime
import json
from decimal import Decimal
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.contrib import messages
from django.template import loader
from django.contrib.auth import authenticate, login as auth_login
from .models import SupportTicket, TicketMessage
from authapp.models import SellerProfile
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
import math

from .models import Product, Tag
from letsLearn.models import Orders
from letsLearn.models import OrderItems
from django.contrib.auth.models import User
from .forms import CheckoutForm
from .models import RSSSubscriber

######Homepage Links########
def homepage(request):
    #return HttpResponse("Hello World! I'm Home.")
    return render(request, 'home.html')

def subscribe_rss(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(request, "Please enter an email address.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        RSSSubscriber.objects.get_or_create(email=email)
        messages.success(request, "You are subscribed for email updates.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    # if someone hits it with GET, just bounce them back
    return redirect(request.META.get("HTTP_REFERER", "/"))

def productViewer(request):
    return render(request, 'productViewer.html')

def about(request):
    #return HttpResponse("My About page.")
    return render(request, 'about.html')

def buyerHome(request):
    return render(request, 'BuyerHome.html')

def requestRefund(request, order_id):
    if not request.user.is_authenticated:
        return redirect("login")

    order = Orders.objects.filter(id=order_id, user=request.user).first()
    if not order:
        messages.error(request, "Order not found.")
        return redirect("/buyerHome/")

    if order.status == 'R':
        messages.info(request, "Refund already requested or processed.")
        return redirect("/buyerHome/")

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip() or "No reason provided."
        order.status = 'R'  # mark order as refund requested
        order.refund_reason = reason
        order.refund_requested_at = timezone.now()
        order.save()

        messages.success(request, f"Refund request submitted for Order #{order.id}.")
        return redirect("/buyerHome/")

    return render(request, "requestRefund.html", {"order": order})

from django.contrib import messages

from django.utils import timezone
from django.shortcuts import get_object_or_404

def acceptRefund(request, ticket_id):
    if not request.user.is_authenticated:
        return redirect("login")

    # find the related ticket
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    # extract order ID from subject (like "Refund Request for Order #12")
    import re
    match = re.search(r"Order\s*#(\d+)", ticket.subject)
    if not match:
        messages.error(request, "Could not identify the order for this refund.")
        return redirect(f"/replyTicket/{ticket.id}/")

    order_id = int(match.group(1))
    order = get_object_or_404(Orders, id=order_id)

    # ensure this user is the seller
    owns_product = OrderItems.objects.filter(
        order_id=order,
        product_id__seller_id=request.user.id
    ).exists()

    if not owns_product:
        messages.error(request, "You cannot approve refunds for this order.")
        return redirect(f"/replyTicket/{ticket.id}/")

    # mark as refunded
    order.status = 'C'  # closed/refunded
    order.refund_acknowledged = True
    order.save()

    # log the action in the chat
    TicketMessage.objects.create(
        ticket=ticket,
        sender=request.user,
        message="Seller has approved the refund."
    )

    # close the ticket automatically
    ticket.status = "Closed"
    ticket.save()

    messages.success(request, f"Refund for Order #{order.id} approved.")
    return redirect(f"/replyTicket/{ticket.id}/")


def denyRefund(request, ticket_id):
    if not request.user.is_authenticated:
        return redirect("login")

    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    import re
    match = re.search(r"Order\s*#(\d+)", ticket.subject)
    if not match:
        messages.error(request, "Could not identify the order for this refund.")
        return redirect(f"/replyTicket/{ticket.id}/")

    order_id = int(match.group(1))
    order = get_object_or_404(Orders, id=order_id)

    owns_product = OrderItems.objects.filter(
        order_id=order,
        product_id__seller_id=request.user.id
    ).exists()

    if not owns_product:
        messages.error(request, "You cannot deny refunds for this order.")
        return redirect(f"/replyTicket/{ticket.id}/")

    # mark as denied
    order.status = 'F'
    order.refund_acknowledged = True
    order.save()

    TicketMessage.objects.create(
        ticket=ticket,
        sender=request.user,
        message="Seller has denied the refund request."
    )

    ticket.status = "Closed"
    ticket.save()

    messages.success(request, f"Refund for Order #{order.id} denied.")
    return redirect(f"/replyTicket/{ticket.id}/")




def marketplace(request):
    template = loader.get_template("marketplace.html")
    page = request.GET.get("page", 1)
    try:
        page = int(page)
    except ValueError:
        page = 1
    page = max(page, 1)

    products = Product.objects.filter(status="active")[(page - 1) * 12:(page * 12)]

    grid = []
    for row in range(math.ceil(len(products) / 3)):
        row_list = []
        for index in range(3):
            product_index = (row * 3) + index
            if product_index >= len(products):
                break

            p = products[product_index]
            p.display_price = intToPrice(p.price_cents)
            row_list.append(p)

        grid.append(row_list)

    context = {
        'next_page': page + 1,
        'prev_page': page - 1,
        'page': page,
        'grid': grid,
    }
    return HttpResponse(template.render(context, request))



def details(request):
    template = loader.get_template("details.html")
    product = Product.objects.get(id=request.GET.get("product_id"))

    price = f"{product.price_cents / 100:.2f}"

    context = {
        "inStock": 1,
        "product": product,
        "price": price
    }
    return HttpResponse(template.render(context, request))

def addtocart(request):
    product_id = request.GET.get("product_id") or request.POST.get("product_id")
    qty = request.GET.get("qty") or request.POST.get("qty") or 1

    try:
        qty = int(qty)
    except:
        qty = 1

    try:
        p = Product.objects.get(id=product_id, status="active")
    except Product.DoesNotExist:
        return JsonResponse({"success": False, "error": "Invalid product"})


    if p.stock <= 0:
        return JsonResponse({"success": False, "error": "Out of stock"})

    qty = min(qty, p.stock)


    cart = request.session.get("cart", {})
    current = cart.get(str(product_id), 0)


    if current + qty > p.stock:
        return JsonResponse({
            "success": False,
            "error": f"Only {p.stock} available"
        })

    cart[str(product_id)] = current + qty
    request.session["cart"] = cart

    return JsonResponse({"success": True})




def shoppingcart(request):
    template = loader.get_template("cart.html")
    cart = request.session.get("cart", {})
    product_data = []
    total_cents = 0

    # remove qty if product_id passed
    deletion_id = request.GET.get("product_id")
    if deletion_id and deletion_id in cart:
        cart[deletion_id] -= 1
        if cart[deletion_id] <= 0:
            del cart[deletion_id]
        request.session["cart"] = cart

    # Build cart display
    for product_id, qty in list(cart.items()):
        try:
            p = Product.objects.get(id=product_id, status="active")
        except Product.DoesNotExist:
            del cart[product_id]
            request.session["cart"] = cart
            continue

        qty = int(qty)
        line_cents = p.price_cents * qty
        total_cents += line_cents

        product_data.append({
            "title": p.title,
            "quantity": qty,
            "price": f"{line_cents / 100:.2f}",
            "product_id": product_id
        })

    request.session["cart"] = cart

    context = {
        "product_data": product_data,
        "total_price": f"{total_cents / 100:.2f}",
    }
    return HttpResponse(template.render(context, request))



def checkout(request):
    template = loader.get_template("checkout.html")
    cart = request.session.get("cart", {})
    total_price = Decimal("0.00")
    product_data = []

    # sanitize cart and compute totals
    for product_id in list(cart.keys()):
        try:
            p = Product.objects.get(id=product_id, status="active")
        except Product.DoesNotExist:
            del cart[product_id]
            request.session["cart"] = cart
            continue

        qty = max(1, int(cart[product_id]))
        cart[product_id] = qty  # normalize

        # Convert price_cents (int) into Decimal dollars
        item_total = Decimal(p.price_cents) * qty / Decimal("100")
        total_price += item_total

        product_data.append({
            "quantity": qty,
            "title": p.title,
            "price": f"{item_total:.2f}",
            "product_id": product_id
        })

    request.session["cart"] = cart

    # Tax & shipping
    tax = total_price * Decimal("0.07")
    shipping = Decimal("17.00")
    grand_total = total_price + tax + shipping

    context = {
        "form": CheckoutForm(),
        "product_data": product_data,
        "price": f"{total_price:.2f}",
        "tax": f"{tax:.2f}",
        "shipping": f"{shipping:.2f}",
        "total": f"{grand_total:.2f}",
    }

    return HttpResponse(template.render(context, request))

    request.session["cart"] = cart

    tax_cents = int(round(total_price * 0.07))
    shipping_cents = 1700
    total_cents = total_price + tax_cents + shipping_cents

    context = {
        "form": CheckoutForm(),
        "product_data": product_data,
        "price": intToPrice(total_price),
        "tax": intToPrice(tax_cents),
        "shipping": intToPrice(shipping_cents),
        "total": intToPrice(total_cents),
    }
    return HttpResponse(template.render(context, request))

def intToPrice(price_cents):
    return "{:.2f}".format(Decimal(price_cents) / 100)

def placeorder(request):
    template = loader.get_template("placeorder.html")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data["address"]
            cart = request.session.get("cart", {})

            total_price = 0


            order = Orders(
                user=request.user,           # <--- ADD THIS FIELD
                created_at=datetime.now(),
                address=address,
                subtotal_cents=0,
                total_cents=0,
                tax_cents=0,
                shipping_cents=0
            )
            order.save()


            for product_id, qty in cart.items():
                try:
                    p = Product.objects.get(id=product_id, status="active")
                except Product.DoesNotExist:
                    continue

                qty = max(1, int(qty))


                if qty > p.stock:
                    qty = p.stock


                if p.stock <= 0:
                    continue

                line_cents = qty * p.price_cents
                total_price += line_cents

                OrderItems.objects.create(
                    order_id=order,
                    product_id=p,
                    price_cents=p.price_cents,
                    qty=qty,
                    return_requested=False
                )


                p.stock -= qty
                p.save()


            tax_cents = total_price * 7 // 100  # 7%
            shipping_cents = 1300  # $13.00

            order.subtotal_cents = total_price
            order.tax_cents = tax_cents
            order.shipping_cents = shipping_cents
            order.total_cents = total_price + tax_cents + shipping_cents
            order.save()

            # ✅ clear cart after save
            request.session["cart"] = {}

    return HttpResponse(template.render({}, request))





def vieworders(request):
    if not request.user.is_authenticated:
        return redirect("login")

    page = int(request.GET.get("page", 1))
    page = max(page, 1)

    # only fetch user's orders
    orders = Orders.objects.filter(user=request.user).order_by("-created_at")[(page - 1) * 12:(page * 12)]

    # build into 3 column grid (like your old version)
    grid = []
    for row in range(math.ceil(len(orders) / 3)):
        row_list = []
        for index in range(3):
            i = (row * 3) + index
            if i >= len(orders):
                break
            row_list.append(orders[i])
        grid.append(row_list)

    return render(request, "vieworders.html", {
        "grid": grid,
        "page": page,
        "next_page": page + 1,
        "prev_page": page - 1,
    })


def orderdetails(request, order_id):
    order = Orders.objects.get(id=order_id)

    return_id = request.GET.get("order_item_id")
    if return_id is not None:
        try:
            order_item = OrderItems.objects.get(id=return_id, order_id=order)
            order_item.return_requested = True
            order_item.save()
        except OrderItems.DoesNotExist:
            pass

    orderitems = []
    for item in OrderItems.objects.filter(order_id=order.id):
        product = item.product_id
        orderitems.append({
            "item": item,
            "product": product,
            "total": intToPrice(item.qty * item.price_cents)
        })

    prices = [
        intToPrice(order.subtotal_cents),
        intToPrice(order.tax_cents),
        intToPrice(order.shipping_cents),
        intToPrice(order.total_cents),
    ]

    return render(request, "orderdetails.html", {
        "order": order,
        "items": orderitems,
        "formated_prices": prices
    })



######Login Page#########
def login(request):
    return render(request,"login.html")


########Admin Support#########

def productReview(request):
    if not request.user.is_staff:
        return redirect("/home")

    if request.method == "POST":

        # Approve Sellers
        for uid in request.POST.getlist("approve_seller"):
            SellerProfile.objects.filter(user_id=uid).update(is_approved=True, is_seller=True)

        # Reject Sellers
        for uid in request.POST.getlist("reject_seller"):
            SellerProfile.objects.filter(user_id=uid).update(is_approved=False, is_seller=False, is_banned=True)

        # Approve Products
        for pid in request.POST.getlist("approve_product"):
            Product.objects.filter(id=pid).update(status="active")

        # Reject Products
        for pid in request.POST.getlist("reject_product"):
            Product.objects.filter(id=pid).update(status="rejected")

        messages.success(request, "Review decisions processed.")
        return redirect("/productReview/")

    pending_sellers = SellerProfile.objects.filter(is_seller=True, is_approved=False)
    pending_products = Product.objects.filter(status="pending")

    return render(request, "productReview.html", {
        "pending_sellers": pending_sellers,
        "pending_products": pending_products
    })


def processModeration(request):
    if request.method != "POST":
        return redirect("productReview")

    approved_sellers = request.POST.getlist("approve_seller")
    approved_products = request.POST.getlist("approve_product")

    # Approve Sellers
    for user_id in approved_sellers:
        try:
            profile = SellerProfile.objects.get(user__id=user_id)
            profile.is_seller = True
            profile.is_pending = False
            profile.is_approved = True
            profile.save()
        except SellerProfile.DoesNotExist:
            pass

    # Approve Products
    for product_id in approved_products:
        try:
            product = Product.objects.get(id=product_id)
            product.is_approved = True
            product.save()
        except Product.DoesNotExist:
            pass

    messages.success(request, "Approvals processed successfully.")
    return redirect("/productReview/")





def tickets(request):

    if not request.user.is_staff:
        return redirect("/home")

    tickets = SupportTicket.objects.all().order_by("-id")

    return render(request, "tickets.html", {
        "tickets": tickets,
        "role": "Admin"
    })

def closeTicket(request, ticket_id):
    if not request.user.is_staff:
        return redirect("/newTicket/")

    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
    except SupportTicket.DoesNotExist:
        return redirect("/tickets/")

    ticket.status = "Closed"
    ticket.save()

    return redirect(f"/replyTicket/{ticket_id}/")


def replyTicket(request, ticket_id):
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
    except SupportTicket.DoesNotExist:
        return redirect("/newTicket/")


    if request.method == "POST" and ticket.status != "Closed":

        msg = request.POST.get("message") or request.POST.get("response") or ""
        msg = msg.strip()


        if msg == "":
            from django.contrib import messages
            messages.error(request, "Message cannot be empty.")
            return redirect(f"/replyTicket/{ticket_id}/")

        TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=msg
        )


        if request.user.is_staff:
            ticket.status = "Pending User"
        else:
            ticket.status = "Pending Admin"

        ticket.save()
        return redirect(f"/replyTicket/{ticket_id}/")


    ticket_messages = ticket.messages.order_by("timestamp")

    return render(request, "replyTicket.html", {
        "ticket": ticket,
        "messages": ticket_messages
    })




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


def productEdit(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        p = Product.objects.get(id=product_id)

        # verify seller owns product
        if request.user.id != p.seller_id:
            return redirect("/home")

        p.title = request.POST.get("title")
        p.description = request.POST.get("description")

        # handle price
        price_dollars = request.POST.get("price")
        if price_dollars is not None:
            try:
                p.price_cents = int(round(float(price_dollars) * 100))
            except ValueError:
                pass

        # ✅ NEW: Update stock
        stock = request.POST.get("stock")
        if stock is not None:
            try:
                p.stock = int(stock)
            except ValueError:
                pass

        p.save()
        return redirect("/productViewer")

    # GET
    product_id = request.GET.get("product_id")
    p = Product.objects.get(id=product_id)
    if request.user.id != p.seller_id:
        return redirect("/home")
    return render(request, "productedit.html", {"product": p})


def productPage(request):
    return render(request, 'productPage.html')


def newTicket(request):
    user = request.user

    # Determine role
    if user.is_superuser or user.is_staff:
        role = "Admin"
    elif hasattr(user, "sellerprofile") and user.sellerprofile.is_seller:
        role = "Seller"
    else:
        role = "Buyer"

    if request.method == "POST":
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if not message or message.strip() == "":
            messages.error(request, "Message cannot be empty.")
            return redirect("/newTicket/")

        ticket = SupportTicket.objects.create(
            user=user,
            subject=subject,
            description=message,
            status="Open"
        )

        TicketMessage.objects.create(
            ticket=ticket,
            sender=user,
            message=message
        )

        return redirect(f"/replyTicket/{ticket.id}/")


    all_tickets = SupportTicket.objects.filter(user=user).order_by("-id")
    support_tickets = all_tickets.exclude(subject__icontains="refund")
    refund_tickets = all_tickets.filter(subject__icontains="refund")

    return render(request,"newTicket.html",{"tickets": support_tickets,"refunds": refund_tickets,"role": role,})






def buyerHome(request):
    return render(request, 'buyerHome.html')

def newListing(request):
    if not request.user.is_authenticated:
        return redirect("login")

def newListing(request):

    if request.method == "POST":
        productName = request.POST.get("productName")
        productDes = request.POST.get("productDes")
        productPrice = request.POST.get("productPrice")
        stock = request.POST.get("stock")
        selected_tags = request.POST.getlist("tags")

        product = Product.objects.create(
            seller_id=request.user.id,
            title=productName,
            description=productDes,
            price_cents=int(float(productPrice) * 100),
            stock=int(stock)
        )
        if selected_tags:
            product.tags.set(selected_tags)


        image_file = request.FILES.get("images")

        if image_file:
            product.main_image = image_file
            product.save()

        return redirect("/productPage/")


    tags = Tag.objects.all()

    template = loader.get_template("newListing.html")
    return HttpResponse(template.render({"tags": tags}, request))
def productViewer(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    # Only show products the logged-in seller owns
    products = Product.objects.filter(seller_id=request.user.id)

    return render(request, 'productViewer.html', {"products": products})



def searchProducts(request):
    query = request.GET.get('q', '').strip()
    selected_tags = request.GET.getlist("tags")  # get selected tags

    products = Product.objects.filter(status="active")

    # text search
    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    # tag search
    if selected_tags:
        products = products.filter(tags__id__in=selected_tags).distinct()

    # add price formatting for UI
    for p in products:
        p.display_price = f"{p.price_cents / 100:.2f}"

    context = {
        'products': products,
        'query': query,
        'tags': Tag.objects.all(),           # send all tag options
        'selected_tags': selected_tags,      # send selected tag IDs
        'search_performed': bool(query or selected_tags),
    }

    return render(request, 'searchProducts.html', context)


def replyUser(request, ticket_id):
    # Safe ticket lookup
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
    except SupportTicket.DoesNotExist:
        return redirect("/newTicket/")

    # Only ticket owner can reply
    if ticket.user != request.user:
        return HttpResponse("Unauthorized", status=403)

    # No replies if ticket is closed
    if ticket.status == "Closed":
        return redirect("/newTicket/")

    # Handle reply form
    if request.method == "POST":
        user_message = request.POST.get("message")

        # Create reply
        TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=user_message
        )

        # Update status so admin knows they need to respond
        ticket.status = "Pending Admin"
        ticket.save()

        return redirect(f"/replyTicket/{ticket_id}/")

    return redirect(f"/replyTicket/{ticket_id}/")

def webUsers(request):
    if not request.user.is_staff:
        return redirect("/home")

    users = User.objects.all()
    user_data = []

    for u in users:
        profile = getattr(u, "sellerprofile", None)
        role = "Seller" if profile and profile.is_seller else "Buyer"
        is_banned = profile.is_banned if profile else False

        user_data.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": role,
            "is_banned": is_banned
        })

    return render(request, "webUsers.html", {"users": user_data})

def banUser(request, user_id):
    if request.method == "POST":
        user = User.objects.get(id=user_id)

        # Prevent admin ban
        if user.is_superuser:
            messages.error(request, "Admins cannot be banned.")
            return redirect("webUsers")

        profile, _ = SellerProfile.objects.get_or_create(user=user)
        profile.is_banned = True
        profile.save()

        # Refresh so UI reflects instantly
        profile.refresh_from_db()

        messages.success(request, f"{user.username} has been banned.")
    return redirect("webUsers")


def unbanUser(request, user_id):
    if request.method == "POST":
        user = User.objects.get(id=user_id)
        profile, _ = SellerProfile.objects.get_or_create(user=user)
        profile.is_banned = False
        profile.save()
        profile.refresh_from_db()

        messages.success(request, f"{user.username} has been unbanned.")
    return redirect("webUsers")

def sellerOrders(request):
    if not request.user.is_authenticated:
        return redirect("login")

    # you only want orders that contain products owned by this seller
    items = OrderItems.objects.filter(product_id__seller_id=request.user.id)

    # get distinct order ids
    order_ids = set(i.order_id.id for i in items)

    refunds = Orders.objects.filter(orderitems__product_id__seller_id=request.user.id,status='R',refund_acknowledged=False).distinct()

    for r in refunds:
        ticket = SupportTicket.objects.filter(subject__icontains=f"Refund Request for Order #{r.id}").first()

        if not ticket:
            # auto-create ticket so seller & buyer can chat
            ticket = SupportTicket.objects.create(user=r.user,subject=f"Refund Request for Order #{r.id}",description=r.refund_reason or "Refund discussion",status="Open",created_at=timezone.now())

        r.refund_ticket = ticket

    orders = Orders.objects.filter(id__in=order_ids).order_by("-created_at")
    total = 0

    for item in items:
        price = item.price_cents * item.qty
        if not item.seller_paid:
            total += price
        item.formatted_price = intToPrice(price)

    return render(request, "sellerOrders.html", {"items": items, "sum_total": intToPrice(total), "refunds": refunds})




def sellerPayout(request):
    if not request.user.is_authenticated:
        return redirect("login")

    items = OrderItems.objects.filter(
        product_id__seller_id=request.user.id,
        seller_paid=False
    )

    total = 0
    for item in items:
        price = item.price_cents * item.qty
        total += price
        item.formatted_price = intToPrice(price)
        item.seller_paid = True
        item.save()

    return render(request, "sellerOrderDetails.html", {"items": items})

def Tags(request):
    # Only staff/admin should add tags
    if not request.user.is_staff:
        return redirect("/home")

    from letsLearn.models import Tag  # import inside the function to avoid conflicts

    # Handle POST → create a new tag
    if request.method == "POST":
        tagname = request.POST.get("tagname", "").strip()
        if tagname != "":
            Tag.objects.get_or_create(name=tagname)
            messages.success(request, f"Tag '{tagname}' added.")

        return redirect("/tags/")

    # Display all tags
    tags = Tag.objects.all().order_by("name")

    return render(request, "tags.html", {"tags": tags})

def payment_page(request):
    return render(request, "payment.html")

def process_payment(request):
    if request.method != "POST":
        return redirect("/cart/")

    card = request.POST.get("card_number")
    expiry = request.POST.get("expiry")
    cvc = request.POST.get("cvc")

    # Basic validation
    if len(card) not in [15, 16] or not card.isdigit():
        messages.error(request, "Invalid card number.")
        return redirect("/payment/")

    if len(cvc) != 3 or not cvc.isdigit():
        messages.error(request, "Invalid CVC.")
        return redirect("/payment/")

    if card != "4242424242424242":
        messages.error(request, "Card declined. Use 4242 4242 4242 4242.")
        return redirect("/payment/")

    # Payment passed → auto-create order via POST
    return redirect("/payment_success/")

def payment_success(request):
    return render(request, "payment_success.html")
