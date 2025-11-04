
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['id', 'seller_id', 'category_id', 'title', 'description', 'price_cents', 'status', 'main_image_url', 'created_at',  'updated_at']

