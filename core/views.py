from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Certificate, CompanyInfo, Product, Category, Tag


def get_company_context():
    """Получение контекста компании для всех шаблонов"""
    company_info = CompanyInfo.objects.first()
    return {
        'company_info': company_info
    }


def index(request):
    categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')[:6]
    
    certificates = Certificate.objects.filter(is_active=True).order_by('-issued_date')[:6]
    
    achievements = [
        {"number": "25+", "text": "лет на рынке"},
        {"number": "1000+", "text": "выполненных проектов"},
        {"number": "500+", "text": "довольных клиентов"},
        {"number": "100%", "text": "контроль качества"},
    ]

    context = {
        **get_company_context(),
        "categories": categories,
        "certificates": certificates,
        "achievements": achievements,
    }
    return render(request, "index.html", context)


def catalog(request):
    category_slug = request.GET.get("category")
    tag_slug = request.GET.get("tag")
    search_query = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort", "name")  
    
    products = Product.objects.filter(is_active=True)
    
    if category_slug:
        products = products.filter(categories__slug=category_slug)
    
    if tag_slug:
        products = products.filter(tags__slug=tag_slug)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )
    
    if sort_by == "price":
        products = products.filter(price__isnull=False).order_by("price")
    elif sort_by == "-price":
        products = products.filter(price__isnull=False).order_by("-price")
    elif sort_by == "-created_at":
        products = products.order_by("-created_at")
    else:
        products = products.order_by("name")
    
    products = products.distinct()
    
    paginator = Paginator(products, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True).order_by('name')
    tags = Tag.objects.filter(is_active=True).order_by('name')
    
    context = {
        **get_company_context(),
        "page_obj": page_obj,
        "products": page_obj,  
        "categories": categories,
        "tags": tags,
        "current_category": category_slug,
        "current_tag": tag_slug,
        "search_query": search_query,
        "sort_by": sort_by,
        "total_count": paginator.count,
    }
    return render(request, "catalog.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    related_products = Product.objects.filter(
        categories__in=product.categories.all(),
        is_active=True
    ).exclude(id=product.id).distinct()[:4]
    
    context = {
        **get_company_context(),
        "product": product,
        "related_products": related_products,
    }
    return render(request, "product_detail.html", context)


def certificates(request):
    certificates = Certificate.objects.filter(is_active=True).order_by('-issued_date')
    
    paginator = Paginator(certificates, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        **get_company_context(),
        "certificates": page_obj,
        "page_obj": page_obj,
    }
    return render(request, "certificates.html", context)


def about(request):
    company = CompanyInfo.objects.first()
    
    achievements = [
        {"number": "25+", "text": "лет на рынке"},
        {"number": "1000+", "text": "выполненных проектов"},
        {"number": "500+", "text": "довольных клиентов"},
        {"number": "100%", "text": "контроль качества"},
    ]
    
    context = {
        **get_company_context(),
        "company": company,
        "achievements": achievements,
    }
    return render(request, "about.html", context)


def contacts(request):
    company = CompanyInfo.objects.first()
    
    if request.method == 'POST':
        try:
            from .models import ContactForm
            
            # Получаем данные из формы
            name = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            message = request.POST.get('message', '').strip()
            
            # Базовая валидация
            if name and phone:
                contact_form = ContactForm.objects.create(
                    name=name,
                    phone=phone,
                    email=email,
                    message=message,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    referer=request.META.get('HTTP_REFERER', ''),
                )
                
                # send_notification_email(contact_form)
                
                return render(request, "contacts.html", {
                    **get_company_context(),
                    "company": company,
                    "success": True,
                    "message": "Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время."
                })
            else:
                return render(request, "contacts.html", {
                    **get_company_context(),
                    "company": company,
                    "error": True,
                    "message": "Пожалуйста, заполните обязательные поля: имя и телефон."
                })
                
        except Exception as e:
            return render(request, "contacts.html", {
                **get_company_context(),
                "company": company,
                "error": True,
                "message": "Произошла ошибка при отправке заявки. Попробуйте позже."
            })
    
    context = {
        **get_company_context(),
        "company": company,
    }
    return render(request, "contacts.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        categories=category, 
        is_active=True
    ).order_by('sort_order', 'name')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        **get_company_context(),
        "category": category,
        "products": page_obj,
        "page_obj": page_obj,
    }
    return render(request, "category_detail.html", context)


def search_results(request):
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        # Поиск по продуктам
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query),
            is_active=True
        )
        
        # Поиск по категориям
        categories = Category.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        )
        
        results = {
            'products': products[:20],  
            'categories': categories[:10],
            'total_products': products.count(),
            'total_categories': categories.count(),
        }
    
    context = {
        **get_company_context(),
        "query": query,
        "results": results,
    }
    return render(request, "search_results.html", context)


def get_client_ip(request):
    """Получение IP адреса клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip