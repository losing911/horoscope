from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Blog listesi
    path('', views.blog_list, name='blog_list'),
    
    # Kategori
    path('kategori/<slug:slug>/', views.category_posts, name='category'),
    
    # Etiket
    path('etiket/<slug:slug>/', views.tag_posts, name='tag'),
    
    # Blog detay
    path('<slug:slug>/', views.post_detail, name='post_detail'),
    
    # Yorum
    path('<slug:slug>/yorum-ekle/', views.add_comment, name='add_comment'),
    
    # Beğeni (AJAX)
    path('<slug:slug>/begen/', views.like_post, name='like_post'),
]
