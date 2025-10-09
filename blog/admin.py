from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Category, Tag, BlogPost, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Kategori yönetimi"""
    list_display = ['name', 'colored_icon', 'post_count', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Görünüm', {
            'fields': ('icon', 'color', 'order')
        }),
        ('Durum', {
            'fields': ('is_active',)
        }),
    )
    
    def colored_icon(self, obj):
        """Renkli ikon göster"""
        return format_html(
            '<i class="fas {} fa-2x" style="color: {};"></i>',
            obj.icon,
            obj.color
        )
    colored_icon.short_description = 'İkon'
    
    def post_count(self, obj):
        """Yazı sayısı"""
        count = obj.get_post_count()
        url = reverse('admin:blog_blogpost_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} yazı</a>', url, count)
    post_count.short_description = 'Yazı Sayısı'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Etiket yönetimi"""
    list_display = ['name', 'slug', 'post_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        """Yazı sayısı"""
        count = obj.get_post_count()
        return f'{count} yazı'
    post_count.short_description = 'Yazı Sayısı'


class CommentInline(admin.TabularInline):
    """Blog yazısı için yorum inline"""
    model = Comment
    extra = 0
    fields = ['user', 'name', 'content', 'status', 'created_at']
    readonly_fields = ['created_at']
    can_delete = True


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """AI destekli blog yazısı yönetimi"""
    
    list_display = ['title', 'author', 'category', 'status', 'status_badge', 'ai_badge', 
                   'publish_date', 'view_count', 'comment_count', 'is_featured']
    list_filter = ['status', 'ai_generated', 'category', 'is_featured', 
                  'allow_comments', 'publish_date', 'created_at']
    list_editable = ['status', 'is_featured']
    search_fields = ['title', 'content', 'excerpt', 'meta_keywords']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'publish_date'
    
    readonly_fields = ['view_count', 'created_at', 'updated_at', 'reading_time']
    
    inlines = [CommentInline]
    
    fieldsets = (
        ('📝 Temel Bilgiler', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('✍️ İçerik', {
            'fields': ('excerpt', 'content'),
            'description': 'AI ile içerik üretmek için aşağıdaki AI bölümünü kullanın.'
        }),
        ('🖼️ Görsel', {
            'fields': ('featured_image', 'featured_image_alt'),
            'classes': ('collapse',)
        }),
        ('🔍 SEO (AI ile üretilebilir)', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
            'description': 'Bu alanlar AI tarafından otomatik üretilebilir.'
        }),
        ('🤖 AI Bilgileri', {
            'fields': ('ai_generated', 'ai_model', 'ai_prompt'),
            'classes': ('collapse',),
            'description': 'AI ile içerik üretimi için kullanılan bilgiler.'
        }),
        ('📊 Durum ve Ayarlar', {
            'fields': ('status', 'publish_date', 'is_featured', 'allow_comments')
        }),
        ('📈 İstatistikler', {
            'fields': ('view_count', 'reading_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_published', 'make_draft', 'generate_seo_with_ai', 'make_featured']
    
    class Media:
        css = {
            'all': ('admin/css/blog_admin.css',)
        }
        js = ('admin/js/blog_admin.js',)
    
    def status_badge(self, obj):
        """Durum rozeti"""
        colors = {
            'draft': '#6c757d',
            'published': '#28a745',
            'scheduled': '#ffc107',
            'archived': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Durum'
    
    def ai_badge(self, obj):
        """AI rozeti"""
        if obj.ai_generated == 'none':
            return format_html('<span style="color: #6c757d;">Manuel</span>')
        
        colors = {
            'gemini': '#4285f4',
            'openai': '#10a37f',
            'hybrid': '#ff9800',
        }
        icons = {
            'gemini': '🔮',
            'openai': '🤖',
            'hybrid': '✨',
        }
        color = colors.get(obj.ai_generated, '#6c757d')
        icon = icons.get(obj.ai_generated, '📝')
        
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_ai_generated_display()
        )
    ai_badge.short_description = 'AI'
    
    def comment_count(self, obj):
        """Yorum sayısı"""
        count = obj.comments.filter(status='approved').count()
        pending = obj.comments.filter(status='pending').count()
        
        if pending > 0:
            return format_html(
                '{} yorum <span style="background: #ffc107; color: white; '
                'padding: 2px 6px; border-radius: 10px; font-size: 10px;">'
                '{} bekliyor</span>',
                count, pending
            )
        return f'{count} yorum'
    comment_count.short_description = 'Yorumlar'
    
    # Admin actions
    def make_published(self, request, queryset):
        """Seçili yazıları yayınla"""
        updated = queryset.update(status='published', publish_date=timezone.now())
        self.message_user(request, f'{updated} yazı yayınlandı.')
    make_published.short_description = '✅ Seçili yazıları yayınla'
    
    def make_draft(self, request, queryset):
        """Seçili yazıları taslağa al"""
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} yazı taslağa alındı.')
    make_draft.short_description = '📝 Seçili yazıları taslağa al'
    
    def make_featured(self, request, queryset):
        """Seçili yazıları öne çıkar"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} yazı öne çıkarıldı.')
    make_featured.short_description = '⭐ Seçili yazıları öne çıkar'
    
    def generate_seo_with_ai(self, request, queryset):
        """AI ile SEO metaları üret"""
        from .services import BlogAIService
        
        service = BlogAIService()
        count = 0
        
        for post in queryset:
            try:
                seo_data = service.generate_seo_meta(post)
                post.meta_title = seo_data.get('meta_title', post.title)[:60]
                post.meta_description = seo_data.get('meta_description', post.excerpt)[:160]
                post.meta_keywords = seo_data.get('meta_keywords', '')[:200]
                post.save()
                count += 1
            except Exception as e:
                self.message_user(request, f'Hata ({post.title}): {str(e)}', level='ERROR')
        
        if count > 0:
            self.message_user(request, f'{count} yazı için SEO metaları üretildi.')
    generate_seo_with_ai.short_description = '🤖 AI ile SEO metaları üret'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Yorum yönetimi"""
    
    list_display = ['author_name', 'post_title', 'content_preview', 
                   'status_badge', 'created_at']
    list_filter = ['status', 'created_at', 'post']
    search_fields = ['content', 'name', 'email', 'user__username']
    date_hierarchy = 'created_at'
    
    actions = ['approve_comments', 'mark_as_spam', 'delete_comments']
    
    fieldsets = (
        ('Yorum Bilgileri', {
            'fields': ('post', 'user', 'name', 'email', 'content')
        }),
        ('Durum', {
            'fields': ('status', 'parent')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def author_name(self, obj):
        """Yazar adı"""
        return obj.get_author_name()
    author_name.short_description = 'Yazar'
    
    def post_title(self, obj):
        """Blog yazısı"""
        url = reverse('admin:blog_blogpost_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, obj.post.title[:50])
    post_title.short_description = 'Yazı'
    
    def content_preview(self, obj):
        """İçerik önizleme"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'İçerik'
    
    def status_badge(self, obj):
        """Durum rozeti"""
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'spam': '#dc3545',
            'deleted': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Durum'
    
    # Admin actions
    def approve_comments(self, request, queryset):
        """Yorumları onayla"""
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} yorum onaylandı.')
    approve_comments.short_description = '✅ Seçili yorumları onayla'
    
    def mark_as_spam(self, request, queryset):
        """Spam olarak işaretle"""
        updated = queryset.update(status='spam')
        self.message_user(request, f'{updated} yorum spam olarak işaretlendi.')
    mark_as_spam.short_description = '🚫 Spam olarak işaretle'
    
    def delete_comments(self, request, queryset):
        """Yorumları sil"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} yorum silindi.')
    delete_comments.short_description = '🗑️ Seçili yorumları sil'
