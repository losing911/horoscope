"""
AI ile otomatik blog içeriği üretimi
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from blog.models import BlogPost, Category
from blog.services import BlogAIService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'AI ile tarot ve astroloji konularında blog yazıları üret'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Üretilecek blog yazısı sayısı (varsayılan: 5)'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Belirli bir kategori için üret (slug)'
        )
        parser.add_argument(
            '--publish',
            action='store_true',
            help='Üretilen yazıları hemen yayınla'
        )
        parser.add_argument(
            '--author',
            type=str,
            help='Yazar kullanıcı adı (varsayılan: ilk staff kullanıcı)'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        category_slug = options.get('category')
        auto_publish = options['publish']
        author_username = options.get('author')
        
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('  🤖 AI BLOG YAZISI ÜRETİCİ'))
        self.stdout.write('=' * 70)
        
        # Yazar bul
        if author_username:
            try:
                author = User.objects.get(username=author_username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Kullanıcı bulunamadı: {author_username}'))
                return
        else:
            author = User.objects.filter(is_staff=True).first()
            if not author:
                self.stdout.write(self.style.ERROR('Staff kullanıcı bulunamadı!'))
                return
        
        self.stdout.write(f'\n📝 Yazar: {author.username}')
        
        # Kategori bul
        category = None
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug, is_active=True)
                self.stdout.write(f'📂 Kategori: {category.name}')
            except Category.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Kategori bulunamadı: {category_slug}'))
                return
        
        self.stdout.write(f'📊 Hedef: {count} blog yazısı')
        self.stdout.write(f'📢 Durum: {"Yayınla" if auto_publish else "Taslak"}')
        self.stdout.write('')
        
        # Blog konuları (tarot ve astroloji)
        topics = self._get_blog_topics(category)
        
        if not topics:
            self.stdout.write(self.style.ERROR('Blog konuları bulunamadı!'))
            return
        
        # AI servisi
        ai_service = BlogAIService()
        
        success_count = 0
        error_count = 0
        
        for i in range(min(count, len(topics))):
            topic = topics[i]
            
            self.stdout.write('-' * 70)
            self.stdout.write(f'🔮 [{i+1}/{count}] {topic["title"]}')
            
            try:
                # AI ile blog üret
                self.stdout.write('  ⏳ AI ile içerik üretiliyor...')
                blog_data = ai_service.generate_blog_post(
                    topic=topic['title'],
                    category=topic.get('category_name'),
                    keywords=topic.get('keywords'),
                    word_count=800
                )
                
                # Blog oluştur
                post = BlogPost.objects.create(
                    title=blog_data['title'],
                    slug='',  # Auto-generated in save()
                    author=author,
                    category=topic.get('category_obj'),
                    excerpt=blog_data['excerpt'],
                    content=blog_data['content'],
                    meta_title=blog_data['meta_title'],
                    meta_description=blog_data['meta_description'],
                    meta_keywords=blog_data['meta_keywords'],
                    ai_generated='gemini',  # veya openai
                    ai_model=self.get_ai_model(),
                    ai_prompt=f"Konu: {topic['title']}",
                    status='published' if auto_publish else 'draft',
                    publish_date=timezone.now() if auto_publish else timezone.now(),
                    allow_comments=True,
                )
                
                # Etiketleri ekle
                if blog_data.get('suggested_tags'):
                    from blog.models import Tag
                    for tag_name in blog_data['suggested_tags'][:5]:
                        tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
                        post.tags.add(tag)
                
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✅ Başarılı! ID: {post.id}'))
                self.stdout.write(f'  📝 Başlık: {post.title}')
                self.stdout.write(f'  🔗 Slug: {post.slug}')
                self.stdout.write(f'  📊 Durum: {post.get_status_display()}')
                self.stdout.write(f'  ⏱️ Okuma Süresi: {post.reading_time} dakika')
                
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'  ❌ Hata: {str(e)}'))
                logger.error(f'Blog üretim hatası ({topic["title"]}): {e}')
        
        # Özet
        self.stdout.write('')
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('  📊 ÖZET'))
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS(f'✅ Başarılı: {success_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'❌ Hatalı: {error_count}'))
        self.stdout.write('=' * 70)
        self.stdout.write('')
    
    def _get_blog_topics(self, category=None):
        """Blog konuları listesi"""
        
        # Tarot konuları
        tarot_topics = [
            {
                'title': 'Tarot Falı Nasıl Bakılır? Başlangıç Rehberi',
                'category_name': 'Tarot',
                'keywords': ['tarot falı', 'tarot okuma', 'tarot rehberi']
            },
            {
                'title': 'Büyük Arcana Kartları ve Anlamları',
                'category_name': 'Tarot',
                'keywords': ['büyük arcana', 'major arcana', 'tarot kartları']
            },
            {
                'title': 'Aşk Falında Tarot Nasıl Kullanılır?',
                'category_name': 'Tarot',
                'keywords': ['aşk falı', 'tarot aşk', 'ilişki tarot']
            },
            {
                'title': 'Kelt Haç Yayılımı ve Yorumlama Teknikleri',
                'category_name': 'Tarot',
                'keywords': ['kelt haç', 'tarot yayılımı', 'celtic cross']
            },
            {
                'title': 'Günlük Tek Kart Çekimi: Gününüzü Tarot ile Keşfedin',
                'category_name': 'Tarot',
                'keywords': ['günlük tarot', 'tek kart', 'daily card']
            },
        ]
        
        # Astroloji konuları
        astrology_topics = [
            {
                'title': 'Burç Özellikleri: 12 Burcu Tanıyalım',
                'category_name': 'Astroloji',
                'keywords': ['burç özellikleri', 'zodiac', '12 burç']
            },
            {
                'title': 'Yükselen Burç Nedir ve Nasıl Hesaplanır?',
                'category_name': 'Astroloji',
                'keywords': ['yükselen burç', 'ascendant', 'doğum haritası']
            },
            {
                'title': 'Ay Burcu ve Duygusal Dünyamız',
                'category_name': 'Astroloji',
                'keywords': ['ay burcu', 'moon sign', 'duygular']
            },
            {
                'title': 'Retro Gezegenlerin Hayatımıza Etkisi',
                'category_name': 'Astroloji',
                'keywords': ['retro', 'retrograde', 'gezegenler']
            },
            {
                'title': 'Burç Uyumu: Hangi Burçlar Uyumlu?',
                'category_name': 'Astroloji',
                'keywords': ['burç uyumu', 'compatibility', 'ilişki astrolojisi']
            },
        ]
        
        # Genel konular
        general_topics = [
            {
                'title': 'Fal Bakmak Günah mı? Dini Açıdan Bakış',
                'category_name': 'Genel',
                'keywords': ['fal günah', 'din', 'inanç']
            },
            {
                'title': 'Meditasyon ve Tarot: Spiritüel Bir Yolculuk',
                'category_name': 'Spiritüel',
                'keywords': ['meditasyon', 'spiritüellik', 'yoga']
            },
            {
                'title': 'Kristaller ve Tarot: Enerjiyi Güçlendirmek',
                'category_name': 'Spiritüel',
                'keywords': ['kristaller', 'enerji', 'taş']
            },
        ]
        
        # Tüm konuları birleştir
        all_topics = tarot_topics + astrology_topics + general_topics
        
        # Kategori varsa filtrele
        if category:
            all_topics = [t for t in all_topics if t['category_name'] == category.name]
            # Category object ekle
            for topic in all_topics:
                topic['category_obj'] = category
        else:
            # Her konuya category object ekle
            for topic in all_topics:
                cat, _ = Category.objects.get_or_create(
                    name=topic['category_name'],
                    defaults={'is_active': True}
                )
                topic['category_obj'] = cat
        
        return all_topics
    
    def get_ai_model(self):
        """Kullanılan AI modelini döndür"""
        from tarot.models import SiteSettings
        settings = SiteSettings.load()
        
        if settings.default_ai_provider == 'gemini':
            return settings.gemini_model
        elif settings.default_ai_provider == 'openai':
            return settings.openai_model
        
        return 'unknown'
