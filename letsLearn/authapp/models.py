from django.db import models
from django.contrib.auth.models import User

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_seller = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    balance_cents = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.user.username} - (Seller: {self.is_seller}, Banned: {self.is_banned})"



@property
def is_seller(self):
    try:
        return self.sellerprofile.is_seller
    except SellerProfile.DoesNotExist:
        return False

User.add_to_class("is_seller", is_seller)