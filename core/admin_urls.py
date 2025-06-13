from . import admin_views
from django.urls import path

app_name = 'core_admin'

urlpatterns = [
    path('statistics/', admin_views.statistics_view, name='statistics'),
    path('backup/', admin_views.backup_view, name='backup'),
    path('export/products/', admin_views.export_products, name='export_products'),
    path('export/contacts/', admin_views.export_contacts, name='export_contacts'),
]
