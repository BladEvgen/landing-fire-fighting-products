from django.shortcuts import get_object_or_404, render

from .models import Certificate, CompanyInfo, Product, Category, Tag


def index(request):
    company = CompanyInfo.objects.first()
    products = Product.objects.all()[:6]
    return render(request, "index.html", {"company": company, "products": products})


def catalog(request):
    category_slug = request.GET.get("category")
    tag_slug = request.GET.get("tag")
    products = Product.objects.all()
    if category_slug:
        products = products.filter(categories__slug=category_slug)
    if tag_slug:
        products = products.filter(tags__slug=tag_slug)
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(
        request,
        "catalog.html",
        {"products": products, "categories": categories, "tags": tags},
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "product_detail.html", {"product": product})


def certificates(request):
    items = Certificate.objects.all()
    return render(request, "certificates.html", {"certificates": items})


def about(request):
    company = CompanyInfo.objects.first()
    return render(request, "about.html", {"company": company})


def contacts(request):
    company = CompanyInfo.objects.first()
    return render(request, "contacts.html", {"company": company})