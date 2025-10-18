from django.urls import path
from . import views, admin_views

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
    
    # Admin/Yönetim Paneli
    path('admin/dashboard/', admin_views.shop_dashboard, name='admin_dashboard'),
    path('admin/orders/', admin_views.order_management, name='order_management'),
    path('admin/orders/<int:order_id>/', admin_views.order_detail_admin, name='order_detail_admin'),
    path('admin/products/', admin_views.product_management, name='product_management'),
    path('admin/products/<int:product_id>/update-stock/', admin_views.update_product_stock, name='update_product_stock'),
    path('admin/statistics/', admin_views.sales_statistics, name='sales_statistics'),
    path('admin/customers/', admin_views.customer_list, name='customer_list'),
]
