from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from core.admin import CompanyAdminGroup
from django.conf.urls.static import static


urlpatterns = [
    path("grappelli/", include("grappelli.urls")),
    path('admin/company/statistics/', CompanyAdminGroup.statistics_view, name='admin_company_statistics'),
    path('admin/company/backup/', CompanyAdminGroup.backup_view, name='admin_company_backup'),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
