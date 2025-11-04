from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

User = get_user_model()


class Product(models.Model):
    stock = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=40)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    def __str__(self):
        return self.title
    

class Orders(models.Model):
    user_id = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    subtotal_cents = models.IntegerField()
    tax_cents = models.IntegerField()
    shipping_cents = models.IntegerField()
    total_cents = models.IntegerField()
    address = models.TextField()
    created_at = models.DateTimeField()

    class Status(models.TextChoices):
        PLACED = 'P', _("placed")
        PAID = 'A', _("paid")
        FULFILLED = 'F', _("fulfilled")
        REFUNDED = 'R', _("refunded")
        CANCELED = 'C', _("canceled")

    status = models.CharField(
        max_length=1,
        choices=Status,
        default=Status.PLACED,
    )



class SupportTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    response = models.TextField(blank=True, null=True)   # <--- admin reply
    status = models.CharField(max_length=20, default="Open") # Open / Pending / Resolved
    created_at = models.DateTimeField(auto_now_add=True)

class TicketMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.subject} ({self.user.username})"
