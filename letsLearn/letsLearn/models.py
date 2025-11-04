from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

class Product(models.Model): #updated for product related section
    id = models.IntegerField(primary_key=True)

    seller_id = models.DecimalField(max_digits=8, decimal_places=1, default=1)
    category_id = models.DecimalField(max_digits=8, decimal_places=1, default=1)
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price_cents = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status =  models.CharField(max_length=10, default = 'active')
    main_image_url = models.TextField(blank=True, null=True)
   
    created_at = models.TextField(blank=True, null=True)
    updated_at = models.TextField(blank=True, null=True)
    class Meta:
        db_table = 'products'
    def __str__(self):
        return self.name


class Orders(models.Model):
    #user_id = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
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
        choices=Status.choices, # initially was choices = Status, but it was giving an error
        default=Status.PLACED,
    )

class OrderItems(models.Model):
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price_cents = models.IntegerField()
    return_requested = models.BooleanField()