from django.db import models
from django.contrib.auth import get_user_model

class Product(models.Model):
    title = models.CharField(max_length=40)
    price = models.IntegerField()
    stock_qty = models.IntegerField()
    description = models.TextField()

class Cart(models.Model):
    user_id = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()