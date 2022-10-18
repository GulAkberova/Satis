from unicodedata import category
from django import forms
from .models import Product,Category


class ProductForm(forms.ModelForm):
    category=forms.ModelChoiceField(
        queryset=Category.objects.order_by("-created_at")
    )



    class Meta:
        model=Product
        exclude=("user", )