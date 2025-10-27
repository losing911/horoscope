"""
Printify ürünlerini senkronize etme management command'ı
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from shop.printify_service import PrintifyService
from shop.models import Category, PrintifySettings


class Command(BaseCommand):
    help = 'Printify\'dan ürünleri senkronize eder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--category-id',
            type=int,
            help='Belirli bir kategoriye import et (ID)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maksimum ürün sayısı (varsayılan: 50)'
        )
        parser.add_argument(
            '--test-connection',
            action='store_true',
            help='Sadece API bağlantısını test et'
        )

    def handle(self, *args, **options):
        service = PrintifyService()
        
        # Bağlantı testi
        if options['test_connection']:
            self.stdout.write('Printify API bağlantısı test ediliyor...')
            if service.api.test_connection():
                self.stdout.write(
                    self.style.SUCCESS('✓ Printify API bağlantısı başarılı!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Printify API bağlantısı başarısız!')
                )
            return
        
        # Ayarları kontrol et
        settings = PrintifySettings.get_settings()
        if not settings.api_token:
            raise CommandError('Printify API token tanımlanmamış!')
        
        if not settings.shop_id:
            raise CommandError('Printify Shop ID tanımlanmamış!')
        
        # Kategori kontrolü
        category_id = options.get('category_id')
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                self.stdout.write(f'Hedef kategori: {category.name}')
            except Category.DoesNotExist:
                raise CommandError(f'Kategori bulunamadı: {category_id}')
        
        # Senkronizasyonu başlat
        limit = options.get('limit', 50)
        self.stdout.write(f'Printify ürün senkronizasyonu başlatılıyor... (Limit: {limit})')
        
        sync_log = service.sync_products_from_printify(
            category_id=category_id,
            limit=limit
        )
        
        # Sonuçları göster
        if sync_log.status == 'completed':
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Senkronizasyon tamamlandı!\n'
                    f'  Toplam: {sync_log.total_items}\n'
                    f'  Başarılı: {sync_log.successful_items}\n'
                    f'  Başarısız: {sync_log.failed_items}\n'
                    f'  Süre: {sync_log.duration_seconds} saniye'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'✗ Senkronizasyon başarısız!\n'
                    f'  Hata: {sync_log.error_message}'
                )
            )