from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    """Blog kategorileri"""
    name = models.CharField('Kategori Adı', max_length=100, unique=True)
    slug = models.SlugField('URL', max_length=100, unique=True, blank=True)
    description = models.TextField('Açıklama', blank=True)
    icon = models.CharField('İkon (Font Awesome)', max_length=50, default='fa-folder', 
                           help_text='Örnek: fa-star, fa-moon, fa-sun')
    color = models.CharField('Renk Kodu', max_length=7, default='#6B1B3D',
                            help_text='Hex renk kodu (örn: #6B1B3D)')
    order = models.PositiveIntegerField('Sıralama', default=0)
    is_active = models.BooleanField('Aktif', default=True)
    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})
    
    def get_post_count(self):
        return self.posts.filter(status='published').count()


class Tag(models.Model):
    """Blog etiketleri"""
    name = models.CharField('Etiket Adı', max_length=50, unique=True)
    slug = models.SlugField('URL', max_length=50, unique=True, blank=True)
    
    class Meta:
        verbose_name = 'Etiket'
        verbose_name_plural = 'Etiketler'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:tag', kwargs={'slug': self.slug})
    
    def get_post_count(self):
        return self.posts.filter(status='published').count()


class BlogPost(models.Model):
    """AI destekli blog yazıları"""
    
    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('published', 'Yayınlandı'),
        ('scheduled', 'Zamanlandı'),
        ('archived', 'Arşivlendi'),
    ]
    
    AI_GENERATION_CHOICES = [
        ('none', 'Manuel'),
        ('gemini', 'Gemini AI'),
        ('openai', 'OpenAI'),
        ('hybrid', 'Hibrit (AI + Manuel)'),
    ]
    
    # Temel bilgiler
    title = models.CharField('Başlık', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
                              related_name='blog_posts', verbose_name='Yazar')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, 
                                 null=True, related_name='posts', verbose_name='Kategori')
    tags = models.ManyToManyField(Tag, related_name='posts', 
                                  blank=True, verbose_name='Etiketler')
    
    # İçerik
    excerpt = models.TextField('Özet', max_length=300, 
                              help_text='Kısa özet (AI tarafından üretilebilir)')
    content = models.TextField('İçerik')
    
    # Görsel
    featured_image = models.ImageField('Öne Çıkan Görsel', 
                                      upload_to='blog/images/%Y/%m/', 
                                      blank=True, null=True)
    featured_image_alt = models.CharField('Görsel Alt Metni', max_length=200, blank=True)
    
    # SEO (AI tarafından üretilebilir)
    meta_title = models.CharField('Meta Başlık', max_length=60, blank=True,
                                  help_text='SEO için sayfa başlığı')
    meta_description = models.CharField('Meta Açıklama', max_length=160, blank=True,
                                       help_text='Arama motorları için açıklama')
    meta_keywords = models.CharField('Anahtar Kelimeler', max_length=200, blank=True,
                                    help_text='Virgülle ayrılmış')
    
    # AI Bilgileri
    ai_generated = models.CharField('AI Üretimi', max_length=20, 
                                   choices=AI_GENERATION_CHOICES, default='none')
    ai_prompt = models.TextField('AI Prompt', blank=True,
                                help_text='İçerik üretimi için kullanılan prompt')
    ai_model = models.CharField('AI Model', max_length=50, blank=True,
                               help_text='Kullanılan AI modeli')
    
    # Durum ve tarihler
    status = models.CharField('Durum', max_length=20, 
                            choices=STATUS_CHOICES, default='draft')
    publish_date = models.DateTimeField('Yayın Tarihi', default=timezone.now)
    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme', auto_now=True)
    
    # İstatistikler
    view_count = models.PositiveIntegerField('Görüntülenme', default=0)
    like_count = models.PositiveIntegerField('Beğeni', default=0)
    
    # Ayarlar
    allow_comments = models.BooleanField('Yorumlara İzin Ver', default=True)
    is_featured = models.BooleanField('Öne Çıkan', default=False,
                                     help_text='Ana sayfada görünsün mü?')
    reading_time = models.PositiveIntegerField('Okuma Süresi (dk)', default=5,
                                              help_text='Ortalama okuma süresi')
    
    class Meta:
        verbose_name = 'Blog Yazısı'
        verbose_name_plural = 'Blog Yazıları'
        ordering = ['-publish_date', '-created_at']
        indexes = [
            models.Index(fields=['-publish_date', 'status']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Slug oluştur
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        
        # Meta title yoksa title kullan
        if not self.meta_title:
            self.meta_title = self.title[:60]
        
        # Meta description yoksa excerpt kullan
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
        
        # Okuma süresini hesapla (ortalama 200 kelime/dk)
        word_count = len(self.content.split())
        self.reading_time = max(1, round(word_count / 200))
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def is_published(self):
        return self.status == 'published' and self.publish_date <= timezone.now()
    
    def get_related_posts(self, limit=3):
        """Benzer yazılar (aynı kategori veya etiketler)"""
        posts = BlogPost.objects.filter(
            status='published',
            publish_date__lte=timezone.now()
        ).exclude(id=self.id)
        
        # Önce aynı kategorideki yazılar
        if self.category:
            posts = posts.filter(category=self.category)
        
        # Sonra aynı etiketlere sahip yazılar
        if self.tags.exists():
            posts = posts.filter(tags__in=self.tags.all()).distinct()
        
        return posts[:limit]
    
    def increment_view_count(self):
        """Görüntülenme sayısını artır"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class Comment(models.Model):
    """Blog yorumları"""
    
    STATUS_CHOICES = [
        ('pending', 'Onay Bekliyor'),
        ('approved', 'Onaylandı'),
        ('spam', 'Spam'),
        ('deleted', 'Silindi'),
    ]
    
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, 
                            related_name='comments', verbose_name='Yazı')
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                           related_name='blog_comments', verbose_name='Kullanıcı',
                           null=True, blank=True)
    
    # Misafir kullanıcılar için
    name = models.CharField('İsim', max_length=100, blank=True)
    email = models.EmailField('E-posta', blank=True)
    
    content = models.TextField('Yorum')
    status = models.CharField('Durum', max_length=20, 
                            choices=STATUS_CHOICES, default='pending')
    
    # Yanıtlama özelliği
    parent = models.ForeignKey('self', on_delete=models.CASCADE, 
                              null=True, blank=True, related_name='replies',
                              verbose_name='Üst Yorum')
    
    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme', auto_now=True)
    
    class Meta:
        verbose_name = 'Yorum'
        verbose_name_plural = 'Yorumlar'
        ordering = ['-created_at']
    
    def __str__(self):
        author = self.user.username if self.user else self.name
        return f'{author} - {self.post.title[:30]}'
    
    def get_author_name(self):
        """Yorum yazarının adını döndür"""
        return self.user.username if self.user else self.name
    
    def is_approved(self):
        return self.status == 'approved'
