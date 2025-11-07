from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

User = get_user_model()


class Product(models.Model):
    id = models.AutoField(primary_key=True)

    seller_id = models.IntegerField(default=1)  
    category_id = models.IntegerField(default=1)

    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    price_cents = models.IntegerField(default=0)  

    stock = models.IntegerField(default=0) 

    status = models.CharField(max_length=10, default='active')
    main_image_url = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)
    
    main_image = models.ImageField(upload_to='product_images/', blank=True, null=True, default='default_product.jpg')

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.title or "Untitled Product"

class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    subtotal_cents = models.IntegerField()
    tax_cents = models.IntegerField()
    shipping_cents = models.IntegerField()
    total_cents = models.IntegerField()
    address = models.TextField()
    created_at = models.DateTimeField()
    
    @property
    def total_dollars(self):
        return self.total_cents / 100

    class Status(models.TextChoices):
        PLACED = 'P', _("placed")
        PAID = 'A', _("paid")
        FULFILLED = 'F', _("fulfilled")
        REFUNDED = 'R', _("refunded")
        CANCELED = 'C', _("canceled")

    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.PLACED,
    )


class SupportTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    response = models.TextField(blank=True, null=True)   
    status = models.CharField(max_length=20, default="Open")
    created_at = models.DateTimeField(auto_now_add=True)

class TicketMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.subject} ({self.user.username})"
class OrderItems(models.Model):
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price_cents = models.IntegerField()
    return_requested = models.BooleanField()

