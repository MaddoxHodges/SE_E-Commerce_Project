from django.contrib import admin
from .models import Product

@admin.action(description="Approve selected products")
def approve_products(modeladmin, request, queryset):
    queryset.update(status="active")

@admin.action(description="Reject selected products")
def reject_products(modeladmin, request, queryset):
    queryset.update(status="rejected")

class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "seller_id", "status", "price_cents", "stock")
    list_filter = ("status",)
    search_fields = ("title", "description")
    actions = [approve_products, reject_products]

admin.site.register(Product, ProductAdmin)
