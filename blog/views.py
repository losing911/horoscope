from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from .models import BlogPost, Category, Tag, Comment
from .forms import CommentForm


def blog_list(request):
    """Blog yazıları listesi"""
    
    # Filtreleme
    posts = BlogPost.objects.filter(
        status='published',
        publish_date__lte=timezone.now()
    ).select_related('author', 'category').prefetch_related('tags')
    
    # Arama
    search_query = request.GET.get('q', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(meta_keywords__icontains=search_query)
        )
    
    # Kategori filtresi
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Tag filtresi
    tag_slug = request.GET.get('tag')
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    
    # Sıralama
    sort = request.GET.get('sort', 'latest')
    if sort == 'popular':
        posts = posts.order_by('-view_count', '-publish_date')
    elif sort == 'oldest':
        posts = posts.order_by('publish_date')
    else:  # latest
        posts = posts.order_by('-publish_date')
    
    # Sayfalama
    paginator = Paginator(posts, 9)  # 9 yazı per sayfa
    page = request.GET.get('page')
    posts_page = paginator.get_page(page)
    
    # Sidebar verileri
    featured_posts = BlogPost.objects.filter(
        status='published',
        is_featured=True,
        publish_date__lte=timezone.now()
    ).order_by('-publish_date')[:3]
    
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('order', 'name')
    
    popular_tags = Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('-post_count')[:10]
    
    context = {
        'title': 'Blog - Tarot ve Astroloji',
        'posts': posts_page,
        'featured_posts': featured_posts,
        'categories': categories,
        'popular_tags': popular_tags,
        'search_query': search_query,
        'current_sort': sort,
    }
    
    return render(request, 'blog/blog_list.html', context)


def post_detail(request, slug):
    """Blog yazısı detay sayfası"""
    
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        status='published',
        publish_date__lte=timezone.now()
    )
    
    # Görüntülenme sayısını artır
    post.increment_view_count()
    
    # Yorumlar
    comments = post.comments.filter(
        status='approved',
        parent__isnull=True  # Sadece ana yorumlar
    ).select_related('user').prefetch_related('replies').order_by('-created_at')
    
    # Yorum formu
    comment_form = CommentForm()
    
    # İlgili yazılar
    related_posts = post.get_related_posts(limit=3)
    
    # Önceki ve sonraki yazı
    prev_post = BlogPost.objects.filter(
        status='published',
        publish_date__lt=post.publish_date
    ).order_by('-publish_date').first()
    
    next_post = BlogPost.objects.filter(
        status='published',
        publish_date__gt=post.publish_date
    ).order_by('publish_date').first()
    
    context = {
        'title': post.meta_title or post.title,
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'related_posts': related_posts,
        'prev_post': prev_post,
        'next_post': next_post,
    }
    
    return render(request, 'blog/post_detail.html', context)


def category_posts(request, slug):
    """Kategoriye göre blog yazıları"""
    
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    posts = BlogPost.objects.filter(
        category=category,
        status='published',
        publish_date__lte=timezone.now()
    ).select_related('author', 'category').order_by('-publish_date')
    
    # Sayfalama
    paginator = Paginator(posts, 9)
    page = request.GET.get('page')
    posts_page = paginator.get_page(page)
    
    # Sidebar
    categories = Category.objects.filter(is_active=True).order_by('order', 'name')
    
    context = {
        'title': f'{category.name} - Blog',
        'category': category,
        'posts': posts_page,
        'categories': categories,
    }
    
    return render(request, 'blog/category_posts.html', context)


def tag_posts(request, slug):
    """Etikete göre blog yazıları"""
    
    tag = get_object_or_404(Tag, slug=slug)
    
    posts = BlogPost.objects.filter(
        tags=tag,
        status='published',
        publish_date__lte=timezone.now()
    ).select_related('author', 'category').order_by('-publish_date')
    
    # Sayfalama
    paginator = Paginator(posts, 9)
    page = request.GET.get('page')
    posts_page = paginator.get_page(page)
    
    # Sidebar
    popular_tags = Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('-post_count')[:10]
    
    context = {
        'title': f'#{tag.name} - Blog',
        'tag': tag,
        'posts': posts_page,
        'popular_tags': popular_tags,
    }
    
    return render(request, 'blog/tag_posts.html', context)


@login_required
def add_comment(request, slug):
    """Blog yazısına yorum ekle"""
    
    if request.method != 'POST':
        return redirect('blog:post_detail', slug=slug)
    
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    if not post.allow_comments:
        messages.error(request, 'Bu yazıya yorum yapılamıyor.')
        return redirect('blog:post_detail', slug=slug)
    
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.status = 'pending'  # Moderasyon için bekliyor
        
        # Parent comment varsa
        parent_id = request.POST.get('parent_id')
        if parent_id:
            parent_comment = Comment.objects.filter(id=parent_id).first()
            if parent_comment:
                comment.parent = parent_comment
        
        comment.save()
        
        messages.success(request, 'Yorumunuz başarıyla eklendi. Onay bekliyor.')
        return redirect('blog:post_detail', slug=slug)
    
    messages.error(request, 'Yorum eklenirken hata oluştu.')
    return redirect('blog:post_detail', slug=slug)


def like_post(request, slug):
    """Blog yazısını beğen (AJAX)"""
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Beğenmek için giriş yapmalısınız.'
        })
    
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Basit like sistemi (gerçek uygulamada ayrı bir model kullanılmalı)
    post.like_count += 1
    post.save(update_fields=['like_count'])
    
    return JsonResponse({
        'success': True,
        'like_count': post.like_count,
        'message': 'Yazıyı beğendiniz!'
    })
