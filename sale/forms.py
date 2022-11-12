from django import forms
from .models import Brand, Product,Category, Subcategory


class ProductForm(forms.ModelForm):
    category=forms.ModelChoiceField(
        queryset=Category.objects.all()
    )
     


    class Meta:
        model=Product
        exclude=("user","subcategory", )


    def __init__(self,*args,**kwargs):
        super(ProductForm,self).__init__(*args,**kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({"class":"form-control"})




class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ("user", "subcategory")

    def __init__(self, *args, **kwargs):
        super(ProductUpdateForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})