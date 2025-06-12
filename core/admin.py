from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Certificate, ContactForm,
    CompanyInfo, Category, Tag, Product, ProductImage, 
)


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'full_name', 'description')
        }),
        ('Контактные данные', {
            'fields': ('phone', 'email', 'address', 'working_hours')
        }),
        ('Реквизиты', {
            'fields': ('inn', 'kpp', 'ogrn', 'bank_details'),
            'classes': ('collapse',)
        }),
        ('SEO настройки', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Hero-секция', {
            'fields': ('hero_title', 'hero_description', 'hero_image'),
            'classes': ('collapse',)
        }),
        ('Призыв к действию', {
            'fields': ('cta_title', 'cta_description'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('founded_year', 'experience_years'),
            'classes': ('collapse',)
        }),
        ('Файлы и документы', {
            'fields': ('requisites_file', 'price_list'),
            'classes': ('collapse',)
        }),
        ('Социальные сети', {
            'fields': ('vk_url', 'telegram_url', 'whatsapp_phone'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Запрещаем создавать больше одной записи
        return not CompanyInfo.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удалять единственную запись
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'sort_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'sort_order')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'image', 'icon')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Настройки', {
            'fields': ('is_active', 'sort_order')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # При редактировании
            return ['created_at', 'updated_at']
        return []


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_preview', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Цвет'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'sort_order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'price_display', 'is_active', 'is_featured', 
        'is_new', 'in_stock', 'created_at'
    )
    list_filter = (
        'is_active', 'is_featured', 'is_new', 'in_stock', 
        'categories', 'tags', 'created_at'
    )
    search_fields = ('name', 'description', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'is_featured', 'is_new', 'in_stock')
    filter_horizontal = ('categories', 'tags')
    inlines = [ProductImageInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'short_description', 'description', 'main_image')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'price_from', 'in_stock')
        }),
        ('Характеристики', {
            'fields': ('specifications',),
            'classes': ('collapse',)
        }),
        ('Категории и теги', {
            'fields': ('categories', 'tags')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Настройки', {
            'fields': ('is_active', 'is_featured', 'is_new', 'sort_order')
        }),
    )
    
    def price_display(self, obj):
        return obj.display_price
    price_display.short_description = 'Цена'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created_at', 'updated_at']
        return []


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'image_preview', 'issued_date', 'expiry_date', 
        'is_expired_display', 'is_active', 'sort_order'
    )
    list_filter = ('is_active', 'issued_date', 'expiry_date')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'sort_order')
    date_hierarchy = 'issued_date'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'image', 'file')
        }),
        ('Даты действия', {
            'fields': ('issued_date', 'expiry_date')
        }),
        ('Настройки', {
            'fields': ('is_active', 'sort_order')
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Превью'
    
    def is_expired_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Истек</span>')
        return format_html('<span style="color: green;">Действует</span>')
    is_expired_display.short_description = 'Статус'


@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    """Админка для заявок"""
    list_display = (
        'name', 'phone', 'email', 'status', 'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone', 'email', 'message')
    list_editable = ('status',)
    readonly_fields = (
        'name', 'phone', 'email', 'message', 
        'ip_address', 'user_agent', 'referer', 'created_at'
    )
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Контактная информация', {
            'fields': ('name', 'phone', 'email', 'message')
        }),
        ('Системная информация', {
            'fields': ('ip_address', 'user_agent', 'referer', 'created_at'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('status',)
        }),
    )
    
    def has_add_permission(self, request):
        return False


# Кастомизация админки
admin.site.site_header = "Админ-панель Вымпел-45"
admin.site.site_title = "Вымпел-45"
admin.site.index_title = "Управление сайтом"

class CompanyGroup:
    """Группа моделей компании"""
    pass

class ProductGroup:
    """Группа моделей продукции"""
    pass

class ContentGroup:
    """Группа контентных моделей"""
    pass