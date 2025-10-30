from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

class Product(models.Model):
    title = models.CharField(max_length=40)
    price = models.IntegerField()
    stock_qty = models.IntegerField()
    description = models.TextField()

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