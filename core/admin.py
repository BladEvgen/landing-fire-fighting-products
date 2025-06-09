from django.contrib import admin

from .models import (
    Tag,
    Product,
    Category,
    Certificate,
    CompanyInfo,
    UserProfile,
    ProductImage,
    PasswordResetToken,
    PasswordResetRequestLog,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ("title", "price")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title",)
    filter_horizontal = ("categories", "tags")


admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Certificate)
admin.site.register(CompanyInfo)
admin.site.register(UserProfile)
admin.site.register(PasswordResetToken)
admin.site.register(PasswordResetRequestLog)