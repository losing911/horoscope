from django.urls import path
from . import views, admin_views, custom_admin_views

app_name = 'shop'

urlpatterns = [
    # Ürün listesi ve detay
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Sepet işlemleri
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Sipariş işlemleri
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    
    # Özel Admin Paneli (Modern UI)
    path('manage/', custom_admin_views.admin_dashboard, name='admin_dashboard'),
    path('manage/products/', custom_admin_views.admin_products, name='admin_products'),
    path('manage/products/add/', custom_admin_views.admin_product_edit, name='admin_product_add'),
    path('manage/products/<int:product_id>/edit/', custom_admin_views.admin_product_edit, name='admin_product_edit'),
    path('manage/orders/', custom_admin_views.admin_orders, name='admin_orders'),
    path('manage/orders/<int:order_id>/', custom_admin_views.admin_order_detail, name='admin_order_detail'),
    path('manage/categories/', custom_admin_views.admin_categories, name='admin_categories'),
    path('manage/eprolo/', custom_admin_views.admin_eprolo, name='admin_eprolo'),
    path('manage/eprolo/settings/', custom_admin_views.admin_eprolo_settings, name='admin_eprolo_settings'),
    path('manage/eprolo/sync/', custom_admin_views.admin_eprolo_sync, name='admin_eprolo_sync'),
    path('manage/statistics/', custom_admin_views.admin_statistics, name='admin_statistics'),
    path('manage/settings/', custom_admin_views.admin_settings, name='admin_settings'),
    
    # Eski Admin Paneli (Yedek)
    path('admin-old/dashboard/', admin_views.shop_dashboard, name='admin_dashboard_old'),
    path('admin-old/orders/', admin_views.order_management, name='order_management'),
    path('admin-old/orders/<int:order_id>/', admin_views.order_detail_admin, name='order_detail_admin'),
    path('admin-old/products/', admin_views.product_management, name='product_management'),
    path('admin-old/products/<int:product_id>/update-stock/', admin_views.update_product_stock, name='update_product_stock'),
    path('admin-old/statistics/', admin_views.sales_statistics, name='sales_statistics'),
    path('admin-old/customers/', admin_views.customer_list, name='customer_list'),
]
