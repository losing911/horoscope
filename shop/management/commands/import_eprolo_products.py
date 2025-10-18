"""
EPROLO Test Ürünlerini İçe Aktar
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Category, Product
from shop.eprollo_service import EprolloAPIService


class Command(BaseCommand):
    help = 'EPROLO test API\'den ürünleri içe aktar'

    def handle(self, *args, **options):
        self.stdout.write("="*60)
        self.stdout.write(self.style.SUCCESS("🛍️  EPROLO TEST ÜRÜN İÇE AKTARMA"))
        self.stdout.write("="*60)
        
        # API servisi
        service = EprolloAPIService()
        
        # Test kategorisi oluştur
        self.stdout.write("\n📂 Kategori oluşturuluyor...")
        category, created = Category.objects.get_or_create(
            slug='test-urunler',
            defaults={
                'name': 'Test Ürünler',
                'description': 'EPROLO test API\'den gelen ürünler',
                'icon': 'fa-flask',
                'is_active': True,
                'order': 99
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"  ✅ Kategori oluşturuldu: {category.name}"))
        else:
            self.stdout.write(f"  ℹ️  Kategori zaten var: {category.name}")
        
        # Ürünleri çek
        self.stdout.write("\n🔄 EPROLO API'den ürünler çekiliyor...")
        result = service.get_products(page=1, pageSize=50)
        
        if not result.get('success'):
            self.stdout.write(self.style.ERROR(f"  ❌ Hata: {result.get('error')}"))
            return
        
        products_data = result.get('data', {}).get('list', [])
        self.stdout.write(self.style.SUCCESS(f"  ✅ {len(products_data)} ürün bulundu"))
        
        # Her ürünü kaydet
        self.stdout.write("\n💾 Ürünler kaydediliyor...")
        created_count = 0
        updated_count = 0
        
        for prod_data in products_data:
            eprolo_id = str(prod_data.get('id'))
            name = prod_data.get('name')
            price = prod_data.get('price', 0)
            main_image = prod_data.get('image', '')
            currency = prod_data.get('currency', 'USD')
            
            # Slug oluştur
            slug = slugify(name, allow_unicode=True)
            
            # Ürün detayını çek (ek görseller için)
            detail_result = service.get_product_detail(eprolo_id)
            images = []
            if detail_result.get('success'):
                images = detail_result.get('data', {}).get('images', [])
            
            # Ürün var mı kontrol et
            product, is_created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    'category': category,
                    'name': name,
                    'description': f'{name}\n\nYüksek kaliteli, dayanıklı malzemeden üretilmiştir. Modern tasarımı ve işlevsel özellikleri ile günlük kullanımınızda size eşlik eder.\n\n• Kaliteli malzeme\n• Uzun ömürlü kullanım\n• Modern tasarım\n• Pratik kullanım',
                    'short_description': f'{name} - Premium kalite',
                    'price': price,
                    'original_price': None,
                    'stock': 999,  # Test için yüksek stok
                    'stock_status': 'in_stock',
                    'image': images[0] if images else main_image,
                    'image_2': images[1] if len(images) > 1 else None,
                    'image_3': images[2] if len(images) > 2 else None,
                    'is_active': True,
                    'is_featured': False,
                    'features': '✓ Premium kalite malzeme\n✓ Hızlı ve güvenli kargo\n✓ 14 gün kolay iade\n✓ Ücretsiz teslimat\n✓ %100 müşteri memnuniyeti'
                }
            )
            
            if is_created:
                created_count += 1
                self.stdout.write(f"  ✅ Eklendi: {name}")
            else:
                updated_count += 1
                self.stdout.write(f"  🔄 Güncellendi: {name}")
        
        # Özet
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📊 ÖZET:"))
        self.stdout.write(f"  • Toplam İşlenen: {len(products_data)}")
        self.stdout.write(self.style.SUCCESS(f"  • Yeni Eklenen: {created_count}"))
        self.stdout.write(f"  • Güncellenen: {updated_count}")
        self.stdout.write(f"  • Kategori: {category.name}")
        self.stdout.write("="*60)
        
        # Ek bilgi - Ürün detayı örneği
        if products_data:
            self.stdout.write("\n🔍 İlk ürünün detayını kontrol edelim...")
            first_product = products_data[0]
            detail_result = service.get_product_detail(first_product.get('id'))
            
            if detail_result.get('success'):
                detail = detail_result.get('data', {})
                self.stdout.write(self.style.SUCCESS("\n✅ Ürün Detay Örneği:"))
                self.stdout.write(f"  ID: {detail.get('id')}")
                self.stdout.write(f"  İsim: {detail.get('name')}")
                self.stdout.write(f"  Fiyat: {detail.get('currency')} {detail.get('price')}")
                self.stdout.write(f"  Stok: {detail.get('stock')}")
                self.stdout.write(f"  Görseller: {len(detail.get('images', []))}")
                self.stdout.write(f"  Varyantlar: {len(detail.get('variants', []))}")
        
        self.stdout.write("\n" + self.style.SUCCESS("✨ İşlem tamamlandı!"))
