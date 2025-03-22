from django.shortcuts import render,get_object_or_404
from store import  models  as store_models

# Create your views here.

def index(request):
    products = store_models.Product.objects.filter(status='published')
    context = {
        'products': products
    }
    return render(request,"store/store.html",context)
    
def product_detail(request, slug):
    product = store_models.Product.objects.get(status="published", slug=slug)
    related_products = store_models.Product.objects.filter(category=product.category,status="published").exclude(id=product.id)
    product_stock_range = range(1, product.stock + 1)
    context = {
        'product': product,
        'related_products': related_products,
        'product_stock_range': product_stock_range,
    }
    return render(request, "store/product_detail.html", context)