from django import forms
from .models import Products,Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields=['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields =['name','description','price','stock','category','image']
