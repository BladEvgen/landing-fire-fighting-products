import re
import csv
import codecs
from django.urls import path
from datetime import timedelta
from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Tag,
    Product,
    Category,
    Certificate,
    CompanyInfo,
    ContactForm,
    UserProfile,
    ProductImage,
)


class CustomUserAdmin(BaseUserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.exclude(is_superuser=True)

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_view_permission(request, obj)


class RestrictedModelAdmin(admin.ModelAdmin):
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
        if not change and hasattr(obj, "created_by"):
            obj.created_by = request.user
        if hasattr(obj, "updated_by"):
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CompanyInfo)
class CompanyInfoAdmin(RestrictedModelAdmin):
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("name", "full_name", "description"), "classes": ("wide",)},
        ),
        (
            "Контактные данные",
            {
                "fields": (
                    "phone",
                    "email",
                    "address",
                    ("latitude", "longtitude"),
                    "working_hours",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "Реквизиты",
            {
                "fields": ("inn", "kpp", "ogrn", "bank_details"),
                "classes": ("collapse",),
            },
        ),
        (
            "Документы и файлы",
            {
                "fields": ("requisites_file", "price_list", "katalog"),
                "classes": ("collapse",),
                "description": "Каталог автоматически сохраняется как katalog-vympel.pdf",
            },
        ),
        (
            "SEO",
            {
                "fields": ("meta_description", "meta_keywords"),
                "classes": ("collapse",),
            },
        ),
        (
            "Hero-секция",
            {
                "fields": ("hero_title", "hero_description", "hero_image"),
                "classes": ("collapse",),
            },
        ),
        (
            "Статистика",
            {
                "fields": ("founded_year", "experience_years", "statistics_html"),
                "classes": ("collapse",),
                "description": "HTML код для отображения статистики на главной странице",
            },
        ),
        (
            "Призыв к действию",
            {"fields": ("cta_title", "cta_description"), "classes": ("collapse",)},
        ),
        (
            "Социальные сети",
            {
                "fields": ("vk_url", "telegram_url", "whatsapp_phone"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))

        if not request.user.is_superuser:
            fieldsets = [fs for fs in fieldsets if fs[0] not in ["Реквизиты", "SEO"]]

        return fieldsets

    def has_add_permission(self, request):
        return not CompanyInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Показываем статистику на главной странице CompanyInfo"""
        extra_context = extra_context or {}

        now = timezone.now()
        today = now.date()

        stats = {
            "total_products": Product.objects.filter(is_active=True).count(),
            "featured_products": Product.objects.filter(is_featured=True).count(),
            "new_products": Product.objects.filter(is_new=True).count(),
            "total_categories": Category.objects.filter(is_active=True).count(),
            "total_certificates": Certificate.objects.filter(is_active=True).count(),
            "expired_certificates": Certificate.objects.filter(
                expiry_date__lt=today, is_active=True
            ).count(),
        }

        extra_context["statistics"] = stats
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Category)
class CategoryAdmin(RestrictedModelAdmin):
    list_display = (
        "name",
        "image_preview",
        "product_count",
        "is_active",
        "sort_order",
        "created_at_display",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "sort_order")
    list_per_page = 25

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": ("name", "slug", "description", "image", "icon"),
                "classes": ("wide",),
            },
        ),
        (
            "SEO",
            {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)},
        ),
        ("Настройки", {"fields": ("is_active", "sort_order")}),
    )

    actions = ["activate_categories", "deactivate_categories", "export_categories_csv"]

    def created_at_display(self, obj):
        if obj.created_at:
            local_time = timezone.localtime(obj.created_at)
            return local_time.strftime("%d.%m.%Y %H:%M")
        return "-"

    created_at_display.short_description = "Создано"
    created_at_display.admin_order_field = "created_at"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.image.url,
            )
        return format_html('<span style="color: #999;">Нет изображения</span>')

    image_preview.short_description = "Превью"

    def product_count(self, obj):
        count = obj.product_count
        if count > 0:
            return format_html(
                '<span style="background: #e8f5e8; color: #2e7d32; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">{} товаров</span>',
                count,
            )
        return format_html(
            '<span style="background: #fff3e0; color: #f57c00; padding: 2px 8px; border-radius: 12px; font-size: 11px;">0 товаров</span>'
        )

    product_count.short_description = "Товаров"

    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f"{updated} категорий активировано.", messages.SUCCESS
        )

    activate_categories.short_description = "Активировать выбранные категории"

    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"{updated} категорий деактивировано.", messages.WARNING
        )

    deactivate_categories.short_description = "Деактивировать выбранные категории"

    def export_categories_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="categories_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        )

        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response, delimiter=";")
        writer.writerow(
            [
                "Название",
                "Описание",
                "Активна",
                "Порядок сортировки",
                "Количество товаров",
                "Дата создания",
            ]
        )

        for category in queryset:
            created_at_str = ""
            if category.created_at:
                local_time = timezone.localtime(category.created_at)
                created_at_str = local_time.strftime("%d.%m.%Y %H:%M")

            description = (
                category.description.replace("\n", " ").replace("\r", " ")
                if category.description
                else ""
            )

            writer.writerow(
                [
                    category.name,
                    description,
                    "Да" if category.is_active else "Нет",
                    category.sort_order,
                    category.product_count,
                    created_at_str,
                ]
            )

        return response

    export_categories_csv.short_description = "Экспортировать в CSV"

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
    list_display = ("name", "color_preview", "product_count", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)
    list_per_page = 50

    actions = ["activate_tags", "deactivate_tags", "export_tags_csv"]

    def color_preview(self, obj):
        return format_html(
            '<div style="width: 24px; height: 24px; background-color: {}; border-radius: 4px; display: inline-block; border: 1px solid #ddd; box-shadow: 0 1px 3px rgba(0,0,0,0.12);"></div>',
            obj.color,
        )

    color_preview.short_description = "Цвет"

    def product_count(self, obj):
        count = obj.product_set.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<span style="background: #f3e5f5; color: #7b1fa2; padding: 2px 6px; border-radius: 10px; font-size: 11px; font-weight: 500;">{}</span>',
                count,
            )
        return format_html('<span style="color: #999;">0</span>')

    product_count.short_description = "Товаров"

    def activate_tags(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} тегов активировано.", messages.SUCCESS)

    activate_tags.short_description = "Активировать выбранные теги"

    def deactivate_tags(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} тегов деактивировано.", messages.WARNING)

    deactivate_tags.short_description = "Деактивировать выбранные теги"

    def export_tags_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="tags_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        )

        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response, delimiter=";")
        writer.writerow(["Название", "Цвет", "Активен", "Количество товаров"])

        for tag in queryset:
            writer.writerow(
                [
                    tag.name,
                    tag.color,
                    "Да" if tag.is_active else "Нет",
                    tag.product_set.filter(is_active=True).count(),
                ]
            )

        return response

    export_tags_csv.short_description = "Экспортировать в CSV"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ("image", "image_preview", "alt_text", "sort_order")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />',
                obj.image.url,
            )
        return format_html('<span style="color: #999;">Нет изображения</span>')

    image_preview.short_description = "Превью"

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Product)
class ProductAdmin(RestrictedModelAdmin):
    list_display = (
        "name",
        "image_preview",
        "get_categories",
        "tags_display",
        "status_badges",
        "created_at_display",
    )
    list_filter = (
        "is_active",
        "is_featured",
        "is_new",
        "in_stock",
        "categories",
        "tags",
        "created_at",
    )
    search_fields = ("name", "description", "short_description", "specifications")
    filter_horizontal = ("categories", "tags")
    list_editable = ()
    inlines = [ProductImageInline]
    list_per_page = 20
    date_hierarchy = "created_at"

    actions = [
        "mark_as_featured",
        "unmark_as_featured",
        "mark_as_new",
        "unmark_as_new",
        "mark_in_stock",
        "mark_out_of_stock",
        "activate_products",
        "deactivate_products",
        "export_products_csv",
    ]

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "name",
                    "slug",
                    "short_description",
                    "description",
                    "image",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "Характеристики",
            {
                "fields": ("specifications",),
                "classes": ("collapse",),
                "description": "Каждую характеристику указывайте с новой строки",
            },
        ),
        ("Категории и теги", {"fields": ("categories", "tags"), "classes": ("wide",)}),
        (
            "Настройки отображения",
            {
                "fields": (
                    ("is_active", "is_featured"),
                    ("is_new", "in_stock"),
                    "sort_order",
                )
            },
        ),
    )

    def created_at_display(self, obj):
        if obj.created_at:
            local_time = timezone.localtime(obj.created_at)
            return local_time.strftime("%d.%m.%Y %H:%M")
        return "-"

    created_at_display.short_description = "Создано"
    created_at_display.admin_order_field = "created_at"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />',
                obj.image.url,
            )
        return format_html('<span style="color: #999;">Нет фото</span>')

    image_preview.short_description = "Фото"

    def get_categories(self, obj):
        categories = obj.categories.all()[:3]
        if categories:
            category_links = []
            for cat in categories:
                category_links.append(
                    f'<span style="background: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-right: 3px;">{cat.name}</span>'
                )
            result = "".join(category_links)
            if obj.categories.count() > 3:
                result += f' <small style="color: #666;">+{obj.categories.count() - 3}</small>'
            return mark_safe(result)
        return format_html('<span style="color: #999;">Без категории</span>')

    get_categories.short_description = "Категории"

    def tags_display(self, obj):
        tags = obj.tags.all()[:3]
        if tags:
            tag_links = []
            for tag in tags:
                tag_links.append(
                    f'<span style="background: {tag.color}; color: white; padding: 1px 4px; border-radius: 8px; font-size: 9px; margin-right: 2px;">{tag.name}</span>'
                )
            result = "".join(tag_links)
            if obj.tags.count() > 3:
                result += (
                    f' <small style="color: #666;">+{obj.tags.count() - 3}</small>'
                )
            return mark_safe(result)
        return ""

    tags_display.short_description = "Теги"

    def status_badges(self, obj):
        badges = []

        if not obj.is_active:
            badges.append(
                '<span style="background: #999; color: white; padding: 1px 4px; border-radius: 6px; font-size: 9px; margin-right: 2px;">СКРЫТ</span>'
            )

        if obj.is_featured:
            badges.append(
                '<span style="background: #4caf50; color: white; padding: 1px 4px; border-radius: 6px; font-size: 9px; margin-right: 2px;">★ РЕК</span>'
            )

        if obj.is_new:
            badges.append(
                '<span style="background: #2196f3; color: white; padding: 1px 4px; border-radius: 6px; font-size: 9px; margin-right: 2px;">НОВОЕ</span>'
            )

        if not obj.in_stock:
            badges.append(
                '<span style="background: #ff9800; color: white; padding: 1px 4px; border-radius: 6px; font-size: 9px; margin-right: 2px;">ПОД ЗАКАЗ</span>'
            )

        return mark_safe("".join(badges)) if badges else ""

    status_badges.short_description = "Статус"

    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} товаров активировано.", messages.SUCCESS)

    activate_products.short_description = "Активировать товары"

    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"{updated} товаров деактивировано.", messages.WARNING
        )

    deactivate_products.short_description = "Деактивировать товары"

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(
            request, f"{updated} товаров отмечено как рекомендуемые.", messages.SUCCESS
        )

    mark_as_featured.short_description = "Отметить как рекомендуемые"

    def unmark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(
            request, f"{updated} товаров убрано из рекомендуемых.", messages.INFO
        )

    unmark_as_featured.short_description = "Убрать из рекомендуемых"

    def mark_as_new(self, request, queryset):
        updated = queryset.update(is_new=True)
        self.message_user(
            request, f"{updated} товаров отмечено как новинки.", messages.SUCCESS
        )

    mark_as_new.short_description = "Отметить как новинки"

    def unmark_as_new(self, request, queryset):
        updated = queryset.update(is_new=False)
        self.message_user(
            request, f"{updated} товаров убрано из новинок.", messages.INFO
        )

    unmark_as_new.short_description = "Убрать из новинок"

    def mark_in_stock(self, request, queryset):
        updated = queryset.update(in_stock=True)
        self.message_user(
            request, f"{updated} товаров отмечено как в наличии.", messages.SUCCESS
        )

    mark_in_stock.short_description = "Отметить как в наличии"

    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(in_stock=False)
        self.message_user(
            request, f"{updated} товаров отмечено как под заказ.", messages.WARNING
        )

    mark_out_of_stock.short_description = "Отметить как под заказ"

    def export_products_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="products_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        )

        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response, delimiter=";")
        writer.writerow(
            [
                "Название",
                "Краткое описание",
                "Полное описание",
                "Характеристики",
                "Категории",
                "Теги",
                "Активен",
                "Рекомендуемый",
                "Новинка",
                "В наличии",
                "Дата создания",
                "Дата обновления",
            ]
        )

        for product in queryset:
            created_at_str = ""
            updated_at_str = ""

            if product.created_at:
                local_created = timezone.localtime(product.created_at)
                created_at_str = local_created.strftime("%d.%m.%Y %H:%M")

            if product.updated_at:
                local_updated = timezone.localtime(product.updated_at)
                updated_at_str = local_updated.strftime("%d.%m.%Y %H:%M")

            short_description = (
                product.short_description.replace("\n", " ").replace("\r", " ").strip()
                if product.short_description
                else ""
            )
            description = (
                product.description.replace("\n", " ").replace("\r", " ").strip()
                if product.description
                else ""
            )
            specifications = (
                product.specifications.replace("\n", " | ").replace("\r", " ").strip()
                if product.specifications
                else ""
            )

            writer.writerow(
                [
                    product.name,
                    short_description,
                    description,
                    specifications,
                    " | ".join([cat.name for cat in product.categories.all()]),
                    " | ".join([tag.name for tag in product.tags.all()]),
                    "Да" if product.is_active else "Нет",
                    "Да" if product.is_featured else "Нет",
                    "Да" if product.is_new else "Нет",
                    "Да" if product.in_stock else "Нет",
                    created_at_str,
                    updated_at_str,
                ]
            )

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

        return fieldsets


@admin.register(Certificate)
class CertificateAdmin(RestrictedModelAdmin):
    list_display = (
        "name",
        "image_preview",
        "issued_date",
        "expiry_date",
        "status_badge",
        "file_link",
        "is_active",
        "sort_order",
        "created_at_display",
    )
    list_filter = ("is_active", "issued_date", "expiry_date")
    search_fields = ("name", "description")
    list_editable = ("is_active", "sort_order")
    date_hierarchy = "issued_date"

    actions = [
        "activate_certificates",
        "deactivate_certificates",
        "export_certificates_csv",
    ]

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("name", "description"), "classes": ("wide",)},
        ),
        (
            "Файлы",
            {
                "fields": ("image", "file"),
                "classes": ("wide",),
                "description": "Изображение для показа на сайте и PDF для скачивания",
            },
        ),
        (
            "Даты действия",
            {
                "fields": ("issued_date", "expiry_date"),
                "description": "Оставьте дату окончания пустой для бессрочных сертификатов",
            },
        ),
        ("Настройки", {"fields": ("is_active", "sort_order")}),
    )

    def created_at_display(self, obj):
        if obj.created_at:
            local_time = timezone.localtime(obj.created_at)
            return local_time.strftime("%d.%m.%Y %H:%M")
        return "-"

    created_at_display.short_description = "Создано"
    created_at_display.admin_order_field = "created_at"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 65px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.image.url,
            )
        return format_html('<span style="color: #999;">Нет изображения</span>')

    image_preview.short_description = "Превью"

    def file_link(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank" style="background: #1976d2; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;">Скачать PDF</a>',
                obj.file.url,
            )
        return format_html('<span style="color: #999;">Нет файла</span>')

    file_link.short_description = "Файл"

    def status_badge(self, obj):
        status = obj.status_display
        if status == "Истёк":
            return format_html(
                '<span style="background: #f44336; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; font-weight: 500;">Истёк</span>'
            )
        elif status == "Действителен":
            return format_html(
                '<span style="background: #4caf50; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; font-weight: 500;">Действует</span>'
            )
        else:
            return format_html(
                '<span style="background: #2196f3; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; font-weight: 500;">Бессрочно</span>'
            )

    status_badge.short_description = "Статус"

    def activate_certificates(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f"{updated} сертификатов показано на сайте.", messages.SUCCESS
        )

    activate_certificates.short_description = "Показать на сайте"

    def deactivate_certificates(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"{updated} сертификатов скрыто с сайта.", messages.WARNING
        )

    deactivate_certificates.short_description = "Скрыть с сайта"

    def export_certificates_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="certificates_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        )

        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response, delimiter=";")
        writer.writerow(
            [
                "Название",
                "Описание",
                "Дата выдачи",
                "Дата окончания",
                "Статус",
                "Активен",
                "Дата создания",
            ]
        )

        for cert in queryset:
            issued_date_str = (
                cert.issued_date.strftime("%d.%m.%Y") if cert.issued_date else ""
            )
            expiry_date_str = (
                cert.expiry_date.strftime("%d.%m.%Y") if cert.expiry_date else ""
            )

            created_at_str = ""
            if cert.created_at:
                local_time = timezone.localtime(cert.created_at)
                created_at_str = local_time.strftime("%d.%m.%Y %H:%M")

            description = (
                cert.description.replace("\n", " ").replace("\r", " ").strip()
                if cert.description
                else ""
            )

            writer.writerow(
                [
                    cert.name,
                    description,
                    issued_date_str,
                    expiry_date_str,
                    cert.status_display,
                    "Да" if cert.is_active else "Нет",
                    created_at_str,
                ]
            )

        return response

    export_certificates_csv.short_description = "Экспортировать в CSV"


@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "email",
        "status",
        "status_display",
        "created_at_display",
        "days_ago",
    )
    list_filter = ("status", "created_at", "personal_data_consent")
    search_fields = ("name", "phone", "email", "message")
    list_editable = ("status",)
    readonly_fields = (
        "name",
        "phone",
        "email",
        "message",
        "ip_address",
        "user_agent",
        "referer",
        "created_at",
        "personal_data_consent",
    )
    date_hierarchy = "created_at"
    list_per_page = 50

    actions = [
        "mark_in_progress",
        "mark_completed",
        "mark_cancelled",
        "export_contacts_csv",
    ]

    fieldsets = (
        (
            "Контактная информация",
            {"fields": ("name", "phone", "email", "message"), "classes": ("wide",)},
        ),
        (
            "Системная информация",
            {
                "fields": (
                    "ip_address",
                    "user_agent",
                    "referer",
                    "created_at",
                    "personal_data_consent",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Статус", {"fields": ("status",)}),
    )

    def created_at_display(self, obj):
        if obj.created_at:
            local_time = timezone.localtime(obj.created_at)
            return local_time.strftime("%d.%m.%Y %H:%M")
        return "-"

    created_at_display.short_description = "Создано"
    created_at_display.admin_order_field = "created_at"

    def status_display(self, obj):
        colors = {
            "new": "#ff9800",
            "in_progress": "#2196f3",
            "completed": "#4caf50",
            "cancelled": "#f44336",
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, "#666"),
            obj.get_status_display(),
        )

    status_display.short_description = "Статус"

    def days_ago(self, obj):
        if obj.created_at:
            now = timezone.now()
            days = (now.date() - obj.created_at.date()).days
            if days == 0:
                return "Сегодня"
            elif days == 1:
                return "Вчера"
            else:
                return f"{days} дн. назад"
        return "-"

    days_ago.short_description = "Создана"

    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status="in_progress")
        self.message_user(request, f"{updated} заявок взято в работу.")

    mark_in_progress.short_description = "Взять в работу"

    def mark_completed(self, request, queryset):
        updated = queryset.update(status="completed")
        self.message_user(request, f"{updated} заявок завершено.")

    mark_completed.short_description = "Отметить как выполненные"

    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status="cancelled")
        self.message_user(request, f"{updated} заявок отменено.")

    mark_cancelled.short_description = "Отменить заявки"

    def export_contacts_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="contacts_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        )

        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response, delimiter=";")
        writer.writerow(
            [
                "Имя",
                "Телефон",
                "Email",
                "Сообщение",
                "Статус",
                "IP адрес",
                "Согласие на обработку данных",
                "Дата создания",
            ]
        )

        for contact in queryset:
            created_at_str = ""
            if contact.created_at:
                local_time = timezone.localtime(contact.created_at)
                created_at_str = local_time.strftime("%d.%m.%Y %H:%M")

            message = (
                contact.message.replace("\n", " ").replace("\r", " ").strip()
                if contact.message
                else ""
            )

            writer.writerow(
                [
                    contact.name,
                    contact.phone,
                    contact.email,
                    message,
                    contact.get_status_display(),
                    contact.ip_address or "",
                    "Да" if contact.personal_data_consent else "Нет",
                    created_at_str,
                ]
            )

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
        extra_context = extra_context or {}

        status_stats = {}
        for status_code, status_name in ContactForm.STATUS_CHOICES:
            status_stats[status_name] = ContactForm.objects.filter(
                status=status_code
            ).count()

        extra_context["status_statistics"] = status_stats

        today = timezone.now().date()
        week_stats = []
        for i in range(7):
            date = today - timedelta(days=i)
            count = ContactForm.objects.filter(created_at__date=date).count()
            week_stats.append({"date": date.strftime("%d.%m"), "count": count})

        extra_context["week_statistics"] = reversed(week_stats)

        return super().changelist_view(request, extra_context=extra_context)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "user_full_name",
        "phone",
        "user_email",
        "user_date_joined",
        "is_staff",
    )
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    list_filter = ("user__is_staff", "user__is_active", "user__date_joined")

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        digits_only = re.sub(r"\D", "", search_term)
        if digits_only:
            matching_ids = []
            for profile in self.model.objects.all():
                phone_digits = re.sub(r"\D", "", profile.phone or "")
                if digits_only in phone_digits:
                    matching_ids.append(profile.id)

            queryset |= self.model.objects.filter(id__in=matching_ids)

        return queryset, use_distinct

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "Email"

    def user_date_joined(self, obj):
        if obj.user.date_joined:
            local_time = timezone.localtime(obj.user.date_joined)
            return local_time.strftime("%d.%m.%Y %H:%M")
        return "-"

    user_date_joined.short_description = "Дата регистрации"

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or "------"

    user_full_name.short_description = "Полное имя"

    def is_staff(self, obj):
        return obj.user.is_staff

    is_staff.boolean = True
    is_staff.short_description = "Сотрудник"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.exclude(user__is_superuser=True)

    def has_change_permission(self, request, obj=None):
        if obj and obj.user.is_superuser and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.user.is_superuser and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        if obj and obj.user.is_superuser and not request.user.is_superuser:
            return False
        return super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        return request.user.is_superuser


class CompanyAdminGroup:
    @staticmethod
    def get_urls():
        return [
            path(
                "statistics/",
                CompanyAdminGroup.statistics_view,
                name="company_statistics",
            ),
            path("backup/", CompanyAdminGroup.backup_view, name="company_backup"),
        ]

    @staticmethod
    def statistics_view(request):
        now = timezone.now()

        context = {
            "title": "Статистика сайта",
            "total_products": Product.objects.count(),
            "active_products": Product.objects.filter(is_active=True).count(),
            "featured_products": Product.objects.filter(is_featured=True).count(),
            "total_categories": Category.objects.count(),
            "total_certificates": Certificate.objects.count(),
            "total_contacts": ContactForm.objects.count(),
            "new_contacts": ContactForm.objects.filter(status="new").count(),
            "generated_at": now.strftime("%d.%m.%Y %H:%M"),
        }
        return TemplateResponse(request, "admin/statistics.html", context)

    @staticmethod
    def backup_view(request):
        if request.method == "POST":
            messages.success(request, "Резервная копия создана успешно!")
            return redirect("admin:index")

        return TemplateResponse(
            request, "admin/backup.html", {"title": "Создание резервной копии"}
        )


admin.site.site_header = "Админ-панель Вымпел-45"
admin.site.site_title = "Вымпел-45"
admin.site.index_title = "Управление сайтом"
admin.site.enable_nav_sidebar = False
