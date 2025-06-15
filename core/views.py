import csv
import json
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q, Count
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Certificate, CompanyInfo, Product, Category, Tag, ContactForm


def get_company_context():
    company_info = CompanyInfo.objects.first()
    return {"company_info": company_info}


def index(request):
    categories = Category.objects.filter(is_active=True).order_by("sort_order", "name")[
        :6
    ]

    certificates = (
        Certificate.objects.filter(is_active=True)
        .filter(Q(expiry_date__isnull=True) | Q(expiry_date__gte=timezone.now().date()))
        .order_by("-issued_date")[:6]
    )

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
    show_featured = request.GET.get("featured") == "1"
    show_new = request.GET.get("new") == "1"

    products = Product.objects.filter(is_active=True).prefetch_related(
        "categories", "tags", "images"
    )

    selected_category = None
    if category_slug:
        try:
            selected_category = Category.objects.get(slug=category_slug, is_active=True)
            products = products.filter(categories=selected_category)
        except Category.DoesNotExist:
            pass

    selected_tag = None
    if tag_slug:
        try:
            selected_tag = Tag.objects.get(slug=tag_slug, is_active=True)
            products = products.filter(tags=selected_tag)
        except Tag.DoesNotExist:
            pass

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(short_description__icontains=search_query)
            | Q(specifications__icontains=search_query)
        )

    if show_featured:
        products = products.filter(is_featured=True)

    if show_new:
        products = products.filter(is_new=True)

    if sort_by == "name":
        products = products.order_by("sort_order", "name")
    elif sort_by == "name_desc":
        products = products.order_by("-name")
    elif sort_by == "featured":
        products = products.order_by("-is_featured", "sort_order", "name")
    elif sort_by == "new":
        products = products.order_by("-is_new", "sort_order", "name")
    else:
        products = products.order_by("sort_order", "name")

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True).order_by("sort_order", "name")
    tags = Tag.objects.filter(is_active=True).order_by("name")

    total_products = Product.objects.filter(is_active=True).count()
    featured_count = Product.objects.filter(is_active=True, is_featured=True).count()
    new_count = Product.objects.filter(is_active=True, is_new=True).count()

    context = {
        **get_company_context(),
        "products": page_obj,
        "categories": categories,
        "tags": tags,
        "selected_category": selected_category,
        "selected_tag": selected_tag,
        "search_query": search_query,
        "sort_by": sort_by,
        "show_featured": show_featured,
        "show_new": show_new,
        "total_products": total_products,
        "featured_count": featured_count,
        "new_count": new_count,
        "products_count": paginator.count,
    }

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "html": render(
                    request, "catalog_products.html", context
                ).content.decode("utf-8"),
                "products_count": paginator.count,
                "page_info": {
                    "has_previous": page_obj.has_previous(),
                    "has_next": page_obj.has_next(),
                    "number": page_obj.number,
                    "num_pages": paginator.num_pages,
                },
            }
        )

    return render(request, "catalog.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    related_products = (
        Product.objects.filter(categories__in=product.categories.all(), is_active=True)
        .exclude(id=product.id)
        .distinct()[:6]
    )

    context = {
        **get_company_context(),
        "product": product,
        "related_products": related_products,
    }

    return render(request, "product_detail.html", context)


def certificates(request):
    certificates = (
        Certificate.objects.filter(is_active=True)
        .filter(Q(expiry_date__isnull=True) | Q(expiry_date__gte=timezone.now().date()))
        .order_by("-issued_date")[:6]
    )
    paginator = Paginator(certificates, 9)
    page_number = request.GET.get("page")
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

    if request.method == "POST":
        try:
            from .models import ContactForm

            name = request.POST.get("name", "").strip()
            phone = request.POST.get("phone", "").strip()
            email = request.POST.get("email", "").strip()
            message = request.POST.get("message", "").strip()
            personal_data_consent = request.POST.get("consent")
            if personal_data_consent == "true":
                personal_data_consent = True
            
            if name and phone and personal_data_consent:
                contact_form = ContactForm.objects.create(
                    name=name,
                    phone=phone,
                    email=email,
                    message=message,
                    personal_data_consent=personal_data_consent,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    referer=request.META.get("HTTP_REFERER", ""),
                )

                # send_notification_email(contact_form)

                return render(
                    request,
                    "contacts.html",
                    {
                        **get_company_context(),
                        "company": company,
                        "success": True,
                        "message": "Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.",
                    },
                )
            else:
                return render(
                    request,
                    "contacts.html",
                    {
                        **get_company_context(),
                        "company": company,
                        "error": True,
                        "message": "Пожалуйста, заполните обязательные поля: имя и телефон.",
                    },
                )

        except Exception:
            return render(
                request,
                "contacts.html",
                {
                    **get_company_context(),
                    "company": company,
                    "error": True,
                    "message": "Произошла ошибка при отправке заявки. Попробуйте позже.",
                },
            )

    context = {
        **get_company_context(),
        "company": company,
    }
    return render(request, "contacts.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(categories=category, is_active=True).order_by(
        "sort_order", "name"
    )

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        **get_company_context(),
        "category": category,
        "products": page_obj,
        "page_obj": page_obj,
    }
    return render(request, "category_detail.html", context)


def search_results(request):
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(short_description__icontains=query),
            is_active=True,
        )

        categories = Category.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query), is_active=True
        )

        results = {
            "products": products[:20],
            "categories": categories[:10],
            "total_products": products.count(),
            "total_categories": categories.count(),
        }

    context = {
        **get_company_context(),
        "query": query,
        "results": results,
    }
    return render(request, "search_results.html", context)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


@staff_member_required
def statistics_view(request):
    
    stats = {
        'total_products': Product.objects.count(),
        'active_products': Product.objects.filter(is_active=True).count(),
        'featured_products': Product.objects.filter(is_featured=True).count(),
        'new_products': Product.objects.filter(is_new=True).count(),
        'out_of_stock': Product.objects.filter(in_stock=False).count(),
        'total_categories': Category.objects.count(),
        'active_categories': Category.objects.filter(is_active=True).count(),
        'total_certificates': Certificate.objects.count(),
        'active_certificates': Certificate.objects.filter(is_active=True).count(),
        'expired_certificates': Certificate.objects.filter(
            expiry_date__lt=datetime.now().date()
        ).count(),
        'total_contacts': ContactForm.objects.count(),
        'new_contacts': ContactForm.objects.filter(status='new').count(),
        'contacts_today': ContactForm.objects.filter(
            created_at__date=datetime.now().date()
        ).count(),
        'contacts_week': ContactForm.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=7)
        ).count(),
    }
    
    week_data = []
    for i in range(7):
        date = datetime.now().date() - timedelta(days=i)
        count = ContactForm.objects.filter(created_at__date=date).count()
        week_data.append({
            'date': date.strftime('%d.%m'),
            'count': count
        })
    
    status_stats = {}
    for status_code, status_name in ContactForm.STATUS_CHOICES:
        status_stats[status_name] = ContactForm.objects.filter(
            status=status_code
        ).count()
    
    top_categories = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('-product_count')[:5]
    
    context = {
        'title': 'Статистика сайта',
        'statistics': stats,
        'week_data': reversed(week_data),
        'status_statistics': status_stats,
        'top_categories': top_categories,
    }
    
    return TemplateResponse(request, 'admin/statistics.html', context)

@staff_member_required 
@require_http_methods(["GET", "POST"])
def backup_view(request):
    
    if request.method == 'POST':
        include_images = request.POST.get('include_images')
        include_contacts = request.POST.get('include_contacts') 
        include_users = request.POST.get('include_users')
        
        try:

            
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'include_images': bool(include_images),
                'include_contacts': bool(include_contacts),
                'include_users': bool(include_users),
                'products_count': Product.objects.count(),
                'categories_count': Category.objects.count(),
                'contacts_count': ContactForm.objects.count() if include_contacts else 0,
            }
            
            response = HttpResponse(
                json.dumps(backup_data, indent=2, ensure_ascii=False),
                content_type='application/json; charset=utf-8'
            )
            response['Content-Disposition'] = f'attachment; filename="backup_metadata_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            
            messages.success(request, 'Резервная копия создана успешно!')
            return response
            
        except Exception as e:
            messages.error(request, f'Ошибка при создании резервной копии: {str(e)}')
            return redirect(request.path)
    
    return TemplateResponse(request, 'admin/backup.html', {
        'title': 'Создание резервной копии'
    })

@staff_member_required
def export_products(request):
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="products_export_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Название', 'Slug', 'Краткое описание', 'Категории', 
        'Теги', 'Активен', 'Рекомендуемый', 'Новинка', 'В наличии',
        'Дата создания', 'Дата обновления'
    ])
    
    for product in Product.objects.all().prefetch_related('categories', 'tags'):
        writer.writerow([
            product.id,
            product.name,
            product.slug,
            product.short_description,
            ', '.join([cat.name for cat in product.categories.all()]),
            ', '.join([tag.name for tag in product.tags.all()]),
            'Да' if product.is_active else 'Нет',
            'Да' if product.is_featured else 'Нет', 
            'Да' if product.is_new else 'Нет',
            'Да' if product.in_stock else 'Нет',
            product.created_at.strftime('%d.%m.%Y %H:%M'),
            product.updated_at.strftime('%d.%m.%Y %H:%M'),
        ])
    
    return response

@staff_member_required
def export_contacts(request):
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="contacts_export_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Имя', 'Телефон', 'Email', 'Сообщение', 'Статус',
        'IP адрес', 'Согласие на обработку данных', 'Дата создания'
    ])
    
    for contact in ContactForm.objects.all():
        writer.writerow([
            contact.id,
            contact.name,
            contact.phone,
            contact.email,
            contact.message,
            contact.get_status_display(),
            contact.ip_address,
            'Да' if contact.personal_data_consent else 'Нет',
            contact.created_at.strftime('%d.%m.%Y %H:%M'),
        ])
    
    return response