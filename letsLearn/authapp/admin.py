from django.contrib import admin
from .models import SellerProfile

class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_seller', 'is_pending', 'is_approved', 'is_banned')
    list_filter = ('is_seller', 'is_pending', 'is_approved', 'is_banned')
    search_fields = ('user__username', 'user__email')

admin.site.register(SellerProfile, SellerProfileAdmin)

