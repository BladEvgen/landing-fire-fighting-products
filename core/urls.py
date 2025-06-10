from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path('', views.index, name='index'),
    
    path('catalog/', views.catalog, name='catalog'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
        
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('certificates/', views.certificates, name='certificates'),
    
    path('search/', views.search_results, name='search_results'),
]