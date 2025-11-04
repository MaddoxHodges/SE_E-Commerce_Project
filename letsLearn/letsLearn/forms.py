from django import forms

class CheckoutForm(forms.Form):
    address = forms.CharField(label="Enter shipping address:")