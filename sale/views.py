from itertools import product
from multiprocessing import context
from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from .models import Brand, Product, Category,Subcategory,ProductImage,Brand,Basket
from django.db.models import Q, F, FloatField
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from .forms import ProductForm,ProductUpdateForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def index_view(request):
    context = {}
    search = request.GET.get("search", None)
    min_price = request.GET.get("min_price", None)
    max_price = request.GET.get("max_price", None)
    subcategory = request.GET.get("subcategory", None)

    products = (
        Product.objects.annotate(
            tax_float_price=Coalesce("tax_price", 0, output_field=FloatField())
        )
        .annotate(
            discount_float_price=Coalesce(
                "discount_price", 0, output_field=FloatField()
            )
        )
        .annotate(
            total_price=F("price") + F("tax_float_price") - F("discount_float_price")
        )
        .order_by("-created_at")
    )

    categories = Category.objects.order_by("-created_at")

    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

        context["search"] = search
        context["products"] = products

    if "button_2" in request.GET:

        if min_price or max_price:
            if min_price:
                products = products.filter(price__gte=float(min_price))
                context["min_price"] = min_price
            if max_price:
                products = products.filter(price__lte=float(max_price))
                context["max_price"] = max_price

        context["products"] = products

    if "subcategory" in request.GET:
        subcategory = request.GET.getlist("subcategory")

        if subcategory:
            products = products.filter(subcategory__id__in=subcategory)
            context["selected_subcategories"] = [int(sub_id) for sub_id in subcategory]
            context["products"] = products

    paginator = Paginator(products, 8)
    page = request.GET.get("page", 1)
    product_list = paginator.get_page(page)

    context["products"] = product_list
    context["paginator"] = paginator
    context["categories"] = categories

    return render(request, "products/product.html", context)

@login_required
def create_view(request):
    product_form = ProductForm()

    if request.method == "POST":
        product_form = ProductForm(request.POST or None)
        images = request.FILES.getlist("image", None)
        subcategory = request.POST.get("subcategory")

        if product_form.is_valid() and images:
            new_product = product_form.save(commit=False)
            new_product.user = request.user
            new_product.subcategory = get_object_or_404(
                Subcategory, id=int(subcategory)
            )
            new_product.save()

            for image in images:
                ProductImage.objects.create(product=new_product, image=image)

            return redirect("sale:index")
        else:
            print(product_form.errors)
    context = {
    
      "product_form":product_form,
    }
    return render(request, "products/create.html", context)


def load_subcategories(request):
    data = {}
    category = request.POST.get("category", None)
    if category:
        subcategories = Subcategory.objects.filter(category__id=int(category))

        data = [
            {"id": subcategory.id, "name": subcategory.name}
            for subcategory in subcategories
        ]
    return JsonResponse({"subcategories": data})


def create_brand_view(request):
    
    brand_name=request.POST.get("brand_name",None)
    new_brand=Brand.objects.create(
      name=brand_name
    )
    data={
      "id":new_brand.id,
      "name":new_brand.name

    }
    return JsonResponse(data)


def update_view(request, slug):
    context = {}
    product = get_object_or_404(Product, slug=slug)
    product_form = ProductUpdateForm(instance=product)
    categories = Category.objects.order_by("-created_at")

    if request.method == "POST":
        product_form = ProductUpdateForm(request.POST or None, instance=product)
        subcategory = request.POST.get("subcategory")
        images = request.FILES.getlist("image", None)

        if product_form.is_valid() and images:
            updated_product = product_form.save(commit=False)
            updated_product.subcategory = get_object_or_404(
                Subcategory, id=int(subcategory)
            )
            updated_product.save()

            for image in images:
                ProductImage.objects.create(product=updated_product, image=image)

            return redirect("sale:index")

    context["product"] = product
    context["product_form"] = product_form
    context["categories"] = categories
    return render(request, "products/update.html", context)




def delete_view(request):
    id = request.POST.get("id")
    product = get_object_or_404(Product, id=int(id))
    product.delete()
    return JsonResponse({})



def user_wishlist_view(request):
    data = {}
    id = request.POST.get("id")
    product = get_object_or_404(Product, id=int(id))

    if request.user in product.wishlist.all():
        data['success'] = False
        product.wishlist.remove(request.user)
    else:
        product.wishlist.add(request.user)
        data['success'] = True

    product.save()
    return JsonResponse(data)


def wishlist_product_view(request):
    context = {}

    products = Product.objects.filter(wishlist__in=[request.user]).annotate(
            tax_float_price=Coalesce("tax_price", 0, output_field=FloatField())
        ).annotate(
            discount_float_price=Coalesce(
                "discount_price", 0, output_field=FloatField()
            )
        ).annotate(
            total_price=F("price") + F("tax_float_price") - F("discount_float_price")
        ).order_by("-created_at")

    context["products"] = products
    return render(request, "products/wishlist.html", context)




def add_basket_view(request):
    data = {}

    id = request.POST.get("id")
    product = get_object_or_404(Product, id=int(id))

    if not Basket.objects.filter(product=product, user=request.user).exists():
        Basket.objects.create(
            product=product, user=request.user
        )

    data['basket_count'] = Basket.objects.filter(user=request.user).count()
    return JsonResponse(data)

def basket_list_view(request):
    context = {}

    baskets = Basket.objects.filter(user=request.user).order_by("-id")
    context['baskets'] = baskets
    return render(request, "products/basket.html", context)


# Class Method

from django.views import View


class ProductListView(View):

 def get(self,request,*args,**kwargs):

    context = {}
    search = request.GET.get("search", None)
    min_price = request.GET.get("min_price", None)
    max_price = request.GET.get("max_price", None)
    subcategory = request.GET.get("subcategory", None)

    products = (
        Product.objects.annotate(
            tax_float_price=Coalesce("tax_price", 0, output_field=FloatField())
        )
        .annotate(
            discount_float_price=Coalesce(
                "discount_price", 0, output_field=FloatField()
            )
        )
        .annotate(
            total_price=F("price") + F("tax_float_price") - F("discount_float_price")
        )
        .order_by("-created_at")
    )

    categories = Category.objects.order_by("-created_at")

    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

        context["search"] = search
        context["products"] = products

    if "button_2" in request.GET:

        if min_price or max_price:
            if min_price:
                products = products.filter(price__gte=float(min_price))
                context["min_price"] = min_price
            if max_price:
                products = products.filter(price__lte=float(max_price))
                context["max_price"] = max_price

        context["products"] = products

    if "subcategory" in request.GET:
        subcategory = request.GET.getlist("subcategory")

        if subcategory:
            products = products.filter(subcategory__id__in=subcategory)
            context["selected_subcategories"] = [int(sub_id) for sub_id in subcategory]
            context["products"] = products

    paginator = Paginator(products, 8)
    page = request.GET.get("page", 1)
    product_list = paginator.get_page(page)

    context["products"] = product_list
    context["paginator"] = paginator
    context["categories"] = categories

    return render(request, "products/product.html", context)


class ProductCreateView(View):

    def get(self,request,*args,**kwargs):
        product_form=ProductForm()
        context={
            "product_form":product_form,
        }
        return render(request, "products/create.html", context)

    def post(self,request,*args,**kwargs):

        context={}
        product_form = ProductForm(request.POST or None)
        images = request.FILES.getlist("image", None)
        subcategory = request.POST.get("subcategory")

        if product_form.is_valid() and images:
            new_product = product_form.save(commit=False)
            new_product.user = request.user
            new_product.subcategory = get_object_or_404(
                Subcategory, id=int(subcategory)
            )
            new_product.save()

            for image in images:
                ProductImage.objects.create(product=new_product, image=image)

            return redirect("sale:index")

        return render(request, "products/create.html", context)
        

