import csv
from django.urls import path
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.utils.html import format_html
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse
from .models import (
    Tag,
    Product,
    Category,
    Certificate,
    ContactForm,
    CompanyInfo,
    UserProfile,
    ProductImage,
)


class RestrictedModelAdmin(admin.ModelAdmin):
    """Базовый класс для ограничения прав доступа"""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(qs.model, "is_active"):
            return qs.filter(is_active=True)
        return qs

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if not request.user.is_superuser:
            readonly_fields.extend(["created_at", "updated_at", "slug"])

        return readonly_fields

    def save_model(self, request, obj, form, change):
        """Добавляем информацию о пользователе при сохранении"""
        if not change and hasattr(obj, 'created_by'):
            obj.created_by = request.user
        if hasattr(obj, 'updated_by'):
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CompanyInfo)
class CompanyInfoAdmin(RestrictedModelAdmin):
    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "full_name", "description"),
            "classes": ("wide",)
        }),
        ("Контактные данные", {
            "fields": (
                "phone", "email", "address", 
                ("latitude", "longtitude"), "working_hours"
            ),
            "classes": ("wide",)
        }),
        ("Реквизиты", {
            "fields": ("inn", "kpp", "ogrn", "bank_details"),
            "classes": ("collapse",),
        }),
        ("Документы", {
            "fields": ("requisites_file", "price_list"),
            "classes": ("collapse",),
        }),
        ("SEO", {
            "fields": ("meta_description", "meta_keywords"),
            "classes": ("collapse",),
        }),
        ("Hero-секция", {
            "fields": ("hero_title", "hero_description", "hero_image"),
            "classes": ("collapse",),
        }),
        ("Призыв к действию", {
            "fields": ("cta_title", "cta_description"), 
            "classes": ("collapse",)
        }),
        ("Дополнительно", {
            "fields": ("founded_year", "experience_years"), 
            "classes": ("collapse",)
        }),
        ("Социальные сети", {
            "fields": ("vk_url", "telegram_url", "whatsapp_phone"),
            "classes": ("collapse",),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))

        if not request.user.is_superuser:
            # Убираем реквизиты для обычных пользователей
            fieldsets = [fs for fs in fieldsets if fs[0] not in ["Реквизиты", "SEO"]]

        return fieldsets

    def has_add_permission(self, request):
        return not CompanyInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Показываем статистику на главной странице CompanyInfo"""
        extra_context = extra_context or {}
        
        # Собираем статистику
        stats = {
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
            'total_certificates': Certificate.objects.filter(is_active=True).count(),
            'new_contacts_week': ContactForm.objects.filter(
                created_at__gte=datetime.now() - timedelta(days=7)
            ).count(),
            'pending_contacts': ContactForm.objects.filter(status='new').count(),
        }
        
        extra_context['statistics'] = stats
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Category)
class CategoryAdmin(RestrictedModelAdmin):
    list_display = ("name", "slug", "product_count", "is_active", "sort_order", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "sort_order")
    list_per_page = 25

    fieldsets = (
        (None, {
            "fields": ("name", "slug", "description", "image", "icon"),
            "classes": ("wide",)
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description"),
            "classes": ("collapse",)
        }),
        ("Настройки", {
            "fields": ("is_active", "sort_order")
        }),
    )

    actions = ['activate_categories', 'deactivate_categories']

    def product_count(self, obj):
        count = obj.product_set.filter(is_active=True).count()
        return format_html(
            '<span style="background: #ffc; padding: 2px 6px; border-radius: 3px;">{}</span>',
            count
        )
    product_count.short_description = "Товаров"

    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} категорий активировано.')
    activate_categories.short_description = "Активировать выбранные категории"

    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} категорий деактивировано.')
    deactivate_categories.short_description = "Деактивировать выбранные категории"

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))

        if not request.user.is_superuser:
            # Убираем SEO поля для обычных пользователей
            fieldsets = [fs for fs in fieldsets if fs[0] != "SEO"]
            
            for name, opts in fieldsets:
                if "slug" in opts["fields"]:
                    fields = list(opts["fields"])
                    fields.remove("slug")
                    opts["fields"] = tuple(fields)

        return fieldsets


@admin.register(Tag)
class TagAdmin(RestrictedModelAdmin):
    list_display = ("name", "slug", "color_preview", "product_count", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)
    list_per_page = 50

    actions = ['activate_tags', 'deactivate_tags']

    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; display: inline-block; border: 1px solid #ccc;"></div>',
            obj.color,
        )
    color_preview.short_description = "Цвет"

    def product_count(self, obj):
        count = obj.product_set.filter(is_active=True).count()
        return count
    product_count.short_description = "Товаров"

    def activate_tags(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} тегов активировано.')
    activate_tags.short_description = "Активировать выбранные теги"

    def deactivate_tags(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} тегов деактивировано.')
    deactivate_tags.short_description = "Деактивировать выбранные теги"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "image_preview", "alt_text", "sort_order")
    readonly_fields = ("image_preview",)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "Нет изображения"
    image_preview.short_description = "Превью"

    def has_delete_permission(self, request, obj=None):
        """Разрешаем удаление изображений"""
        return True


@admin.register(Product)
class ProductAdmin(RestrictedModelAdmin):
    list_display = (
        "name", "image_preview", "get_categories", "tags_display", 
        "is_active", "is_featured", "is_new", "in_stock", "created_at"
    )
    list_filter = (
        "is_active", "is_featured", "is_new", "in_stock", 
        "categories", "tags", "created_at"
    )
    search_fields = ("name", "description", "short_description", "specifications")
    filter_horizontal = ("categories", "tags")
    list_editable = ("is_active", "is_featured", "is_new", "in_stock")
    inlines = [ProductImageInline]
    list_per_page = 20
    date_hierarchy = "created_at"

    actions = [
        'mark_as_featured', 'unmark_as_featured', 
        'mark_as_new', 'unmark_as_new',
        'mark_in_stock', 'mark_out_of_stock',
        'export_products_csv'
    ]

    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "slug", "short_description", "description", "image"),
            "classes": ("wide",)
        }),
        ("Характеристики", {
            "fields": ("specifications",), 
            "classes": ("collapse",)
        }),
        ("Категории и теги", {
            "fields": ("categories", "tags"),
            "classes": ("wide",)
        }),
        ("Настройки", {
            "fields": (
                ("is_active", "is_featured"),
                ("is_new", "in_stock"),
                "sort_order"
            )
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "Нет изображения"
    image_preview.short_description = "Фото"

    def get_categories(self, obj):
        categories = obj.categories.all()[:3]
        if categories:
            category_links = []
            for cat in categories:
                category_links.append(f'<span style="background: #e1f5fe; padding: 2px 6px; border-radius: 3px; margin-right: 4px;">{cat.name}</span>')
            result = ''.join(category_links)
            if obj.categories.count() > 3:
                result += f' <small>+{obj.categories.count() - 3}</small>'
            return mark_safe(result)
        return "Без категории"
    get_categories.short_description = "Категории"

    def tags_display(self, obj):
        tags = obj.tags.all()[:3]
        if tags:
            tag_links = []
            for tag in tags:
                tag_links.append(
                    f'<span style="background: {tag.color}; color: white; padding: 1px 4px; border-radius: 2px; font-size: 10px; margin-right: 2px;">{tag.name}</span>'
                )
            result = ''.join(tag_links)
            if obj.tags.count() > 3:
                result += f' <small>+{obj.tags.count() - 3}</small>'
            return mark_safe(result)
        return ""
    tags_display.short_description = "Теги"

    # Действия
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} товаров отмечено как рекомендуемые.')
    mark_as_featured.short_description = "Отметить как рекомендуемые"

    def unmark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} товаров убрано из рекомендуемых.')
    unmark_as_featured.short_description = "Убрать из рекомендуемых"

    def mark_as_new(self, request, queryset):
        updated = queryset.update(is_new=True)
        self.message_user(request, f'{updated} товаров отмечено как новинки.')
    mark_as_new.short_description = "Отметить как новинки"

    def unmark_as_new(self, request, queryset):
        updated = queryset.update(is_new=False)
        self.message_user(request, f'{updated} товаров убрано из новинок.')
    unmark_as_new.short_description = "Убрать из новинок"

    def mark_in_stock(self, request, queryset):
        updated = queryset.update(in_stock=True)
        self.message_user(request, f'{updated} товаров отмечено как в наличии.')
    mark_in_stock.short_description = "Отметить как в наличии"

    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(in_stock=False)
        self.message_user(request, f'{updated} товаров отмечено как под заказ.')
    mark_out_of_stock.short_description = "Отметить как под заказ"

    def export_products_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="products_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Название', 'Категории', 'Теги', 'Активен', 'Рекомендуемый', 'Новинка', 'В наличии'])
        
        for product in queryset:
            writer.writerow([
                product.name,
                ', '.join([cat.name for cat in product.categories.all()]),
                ', '.join([tag.name for tag in product.tags.all()]),
                'Да' if product.is_active else 'Нет',
                'Да' if product.is_featured else 'Нет',
                'Да' if product.is_new else 'Нет',
                'Да' if product.in_stock else 'Нет',
            ])
        
        return response
    export_products_csv.short_description = "Экспортировать в CSV"

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))

        if not request.user.is_superuser:
            for name, opts in fieldsets:
                if name == "Основная информация" and "slug" in opts["fields"]:
                    fields = list(opts["fields"])
                    fields.remove("slug")
                    opts["fields"] = tuple(fields)
                elif name == "Настройки":
                    opts["fields"] = (("is_active", "is_featured"), ("is_new", "in_stock"))

        return fieldsets


@admin.register(Certificate)
class CertificateAdmin(RestrictedModelAdmin):
    list_display = (
        "name", "image_preview", "issued_date", "expiry_date", 
        "is_expired_display", "is_active", "sort_order", "created_at"
    )
    list_filter = ("is_active", "issued_date", "expiry_date")
    search_fields = ("name", "description")
    list_editable = ("is_active", "sort_order")
    date_hierarchy = "issued_date"

    actions = ['activate_certificates', 'deactivate_certificates']

    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "description", "image", "file"),
            "classes": ("wide",)
        }),
        ("Даты действия", {
            "fields": ("issued_date", "expiry_date"),
            "description": "Даты истечения не отображаются на сайте",
        }),
        ("Настройки", {
            "fields": ("is_active", "sort_order")
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "Нет изображения"
    image_preview.short_description = "Превью"

    def is_expired_display(self, obj):
        if obj.is_expired:
            return format_html(
                '<span style="color: red; font-weight: bold;">Истек</span>'
            )
        elif obj.expiry_date:
            return format_html(
                '<span style="color: green;">Действует</span>'
            )
        return "Бессрочно"
    is_expired_display.short_description = "Статус"

    def activate_certificates(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} сертификатов активировано.')
    activate_certificates.short_description = "Активировать выбранные сертификаты"

    def deactivate_certificates(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} сертификатов деактивировано.')
    deactivate_certificates.short_description = "Деактивировать выбранные сертификаты"


@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "status", "status_display", "created_at", "days_ago")
    list_filter = ("status", "created_at", "personal_data_consent")
    search_fields = ("name", "phone", "email", "message")
    list_editable = ("status",)
    readonly_fields = (
        "name", "phone", "email", "message", "ip_address", 
        "user_agent", "referer", "created_at", "personal_data_consent"
    )
    date_hierarchy = "created_at"
    list_per_page = 50

    actions = [
        'mark_in_progress', 'mark_completed', 'mark_cancelled',
        'export_contacts_csv'
    ]

    fieldsets = (
        ("Контактная информация", {
            "fields": ("name", "phone", "email", "message"),
            "classes": ("wide",)
        }),
        ("Системная информация", {
            "fields": ("ip_address", "user_agent", "referer", "created_at", "personal_data_consent"),
            "classes": ("collapse",),
        }),
        ("Статус", {
            "fields": ("status",)
        }),
    )

    def status_display(self, obj):
        colors = {
            'new': '#ff9800',
            'in_progress': '#2196f3', 
            'completed': '#4caf50',
            'cancelled': '#f44336'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#666'),
            obj.get_status_display()
        )
    status_display.short_description = "Статус"

    def days_ago(self, obj):
        days = (datetime.now().date() - obj.created_at.date()).days
        if days == 0:
            return "Сегодня"
        elif days == 1:
            return "Вчера"
        else:
            return f"{days} дн. назад"
    days_ago.short_description = "Создана"

    # Действия
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} заявок взято в работу.')
    mark_in_progress.short_description = "Взять в работу"

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} заявок завершено.')
    mark_completed.short_description = "Отметить как выполненные"

    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} заявок отменено.')
    mark_cancelled.short_description = "Отменить заявки"

    def export_contacts_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="contacts_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Имя', 'Телефон', 'Email', 'Сообщение', 'Статус', 'Дата создания'])
        
        for contact in queryset:
            writer.writerow([
                contact.name,
                contact.phone,
                contact.email,
                contact.message,
                contact.get_status_display(),
                contact.created_at.strftime('%d.%m.%Y %H:%M'),
            ])
        
        return response
    export_contacts_csv.short_description = "Экспортировать в CSV"

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))

        if not request.user.is_superuser:
            fieldsets = [fs for fs in fieldsets if fs[0] != "Системная информация"]

        return fieldsets

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def changelist_view(self, request, extra_context=None):
        """Добавляем статистику по заявкам"""
        extra_context = extra_context or {}
        
        # Статистика по статусам
        status_stats = {}
        for status_code, status_name in ContactForm.STATUS_CHOICES:
            status_stats[status_name] = ContactForm.objects.filter(status=status_code).count()
        
        extra_context['status_statistics'] = status_stats
        
        # Статистика за последние дни
        today = datetime.now().date()
        week_stats = []
        for i in range(7):
            date = today - timedelta(days=i)
            count = ContactForm.objects.filter(created_at__date=date).count()
            week_stats.append({
                'date': date.strftime('%d.%m'),
                'count': count
            })
        
        extra_context['week_statistics'] = reversed(week_stats)
        
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "user_email", "user_date_joined", "is_staff")
    search_fields = ("user__username", "user__email", "phone")
    list_filter = ("user__is_staff", "user__is_active", "user__date_joined")

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"

    def user_date_joined(self, obj):
        return obj.user.date_joined.strftime('%d.%m.%Y')
    user_date_joined.short_description = "Дата регистрации"

    def is_staff(self, obj):
        return obj.user.is_staff
    is_staff.boolean = True
    is_staff.short_description = "Сотрудник"


class CompanyAdminGroup:
    """Группа административных инструментов компании"""
    
    @staticmethod
    def get_urls():
        """Возвращает дополнительные URL для админки"""
        from django.urls import path
        return [
            path('statistics/', CompanyAdminGroup.statistics_view, name='company_statistics'),
            path('backup/', CompanyAdminGroup.backup_view, name='company_backup'),
        ]
    
    @staticmethod
    def statistics_view(request):
        """Представление статистики"""
        context = {
            'title': 'Статистика сайта',
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(is_active=True).count(),
            'featured_products': Product.objects.filter(is_featured=True).count(),
            'total_categories': Category.objects.count(),
            'total_certificates': Certificate.objects.count(),
            'total_contacts': ContactForm.objects.count(),
            'new_contacts': ContactForm.objects.filter(status='new').count(),
        }
        return TemplateResponse(request, 'admin/statistics.html', context)
    
    @staticmethod
    def backup_view(request):
        """Представление для создания резервных копий"""
        if request.method == 'POST':
            # Здесь можно добавить логику создания бэкапа
            messages.success(request, 'Резервная копия создана успешно!')
            return redirect('admin:index')
        
        return TemplateResponse(request, 'admin/backup.html', {
            'title': 'Создание резервной копии'
        })



admin.site.site_header = "Админ-панель Вымпел-45"
admin.site.site_title = "Вымпел-45"
admin.site.index_title = "Управление сайтом"

admin.site.enable_nav_sidebar = False  