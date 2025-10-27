"""
Printify API entegrasyon servisi
"""
import requests
import json
from datetime import datetime, timezone
from decimal import Decimal
from django.conf import settings
from django.utils import timezone as django_timezone
from .models import PrintifySettings, PrintifySyncLog, Product, Category


class PrintifyAPI:
    """Printify API client"""
    
    def __init__(self):
        self.settings = PrintifySettings.get_settings()
        self.base_url = "https://api.printify.com/v1"
        if self.settings.use_sandbox:
            self.base_url = "https://api.printify.com/v1"  # Printify uses same URL for sandbox
        
        self.headers = {
            'Authorization': f'Bearer {self.settings.api_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'DjTarot/1.0'
        }
    
    def test_connection(self):
        """API bağlantısını test et"""
        try:
            response = requests.get(f"{self.base_url}/shops.json", headers=self.headers, timeout=30)
            return response.status_code == 200
        except Exception as e:
            print(f"Printify API bağlantı hatası: {e}")
            return False
    
    def get_shops(self):
        """Mağazaları getir"""
        try:
            response = requests.get(f"{self.base_url}/shops.json", headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Mağazalar alınırken hata: {e}")
            return None
    
    def get_shop_products(self, shop_id=None, page=1, limit=20):
        """Mağaza ürünlerini getir"""
        if not shop_id:
            shop_id = self.settings.shop_id
        
        try:
            params = {'page': page, 'limit': limit}
            response = requests.get(
                f"{self.base_url}/shops/{shop_id}/products.json",
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ürünler alınırken hata: {e}")
            return None
    
    def get_product_details(self, shop_id, product_id):
        """Ürün detaylarını getir"""
        try:
            response = requests.get(
                f"{self.base_url}/shops/{shop_id}/products/{product_id}.json",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ürün detayları alınırken hata: {e}")
            return None
    
    def create_product(self, shop_id, product_data):
        """Yeni ürün oluştur"""
        try:
            response = requests.post(
                f"{self.base_url}/shops/{shop_id}/products.json",
                headers=self.headers,
                json=product_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ürün oluşturulurken hata: {e}")
            return None
    
    def update_product(self, shop_id, product_id, product_data):
        """Ürünü güncelle"""
        try:
            response = requests.put(
                f"{self.base_url}/shops/{shop_id}/products/{product_id}.json",
                headers=self.headers,
                json=product_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ürün güncellenirken hata: {e}")
            return None
    
    def publish_product(self, shop_id, product_id):
        """Ürünü yayınla"""
        try:
            response = requests.post(
                f"{self.base_url}/shops/{shop_id}/products/{product_id}/publish.json",
                headers=self.headers,
                json={"title": True, "description": True, "images": True, "variants": True, "tags": True, "keyFeatures": True, "shipping_template": True},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ürün yayınlanırken hata: {e}")
            return None
    
    def get_blueprints(self):
        """Mevcut blueprint'leri getir"""
        try:
            response = requests.get(f"{self.base_url}/catalog/blueprints.json", headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Blueprint'ler alınırken hata: {e}")
            return None
    
    def get_print_providers(self, blueprint_id):
        """Blueprint için print provider'ları getir"""
        try:
            response = requests.get(
                f"{self.base_url}/catalog/blueprints/{blueprint_id}/print_providers.json",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Print provider'lar alınırken hata: {e}")
            return None


class PrintifyService:
    """Printify entegrasyon servisi"""
    
    def __init__(self):
        self.api = PrintifyAPI()
        self.settings = PrintifySettings.get_settings()
    
    def sync_products_from_printify(self, category_id=None, limit=50):
        """Printify'dan ürünleri senkronize et"""
        sync_log = PrintifySyncLog.objects.create(
            sync_type='products',
            status='in_progress'
        )
        
        try:
            if not self.settings.shop_id:
                raise Exception("Printify Shop ID tanımlanmamış")
            
            # Ürünleri getir
            products_data = self.api.get_shop_products(
                shop_id=self.settings.shop_id,
                limit=limit
            )
            
            if not products_data:
                raise Exception("Printify'dan ürün verisi alınamadı")
            
            products = products_data.get('data', [])
            sync_log.total_items = len(products)
            sync_log.save()
            
            successful_count = 0
            failed_count = 0
            
            # Kategoriye göre filtrele (eğer belirtilmişse)
            target_category = None
            if category_id:
                try:
                    target_category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    target_category = self.settings.default_category
            else:
                target_category = self.settings.default_category
            
            if not target_category:
                raise Exception("Hedef kategori bulunamadı")
            
            for product_data in products:
                try:
                    self._import_single_product(product_data, target_category)
                    successful_count += 1
                except Exception as e:
                    print(f"Ürün import hatası: {e}")
                    failed_count += 1
            
            sync_log.successful_items = successful_count
            sync_log.failed_items = failed_count
            sync_log.status = 'completed'
            sync_log.completed_at = django_timezone.now()
            
        except Exception as e:
            sync_log.status = 'failed'
            sync_log.error_message = str(e)
            sync_log.completed_at = django_timezone.now()
            print(f"Printify senkronizasyon hatası: {e}")
        
        finally:
            sync_log.save()
            
        return sync_log
    
    def _import_single_product(self, product_data, category):
        """Tek bir ürünü import et"""
        printify_product_id = str(product_data.get('id'))
        
        # Ürün zaten var mı kontrol et
        existing_product = Product.objects.filter(
            printify_product_id=printify_product_id
        ).first()
        
        if existing_product:
            # Mevcut ürünü güncelle
            self._update_product_from_printify(existing_product, product_data)
            return existing_product
        
        # Yeni ürün oluştur
        product = Product()
        product.source = 'printify'
        product.category = category
        product.printify_product_id = printify_product_id
        product.printify_shop_id = str(product_data.get('shop_id', ''))
        product.printify_blueprint_id = str(product_data.get('blueprint_id', ''))
        product.printify_print_provider_id = str(product_data.get('print_provider_id', ''))
        product.printify_status = product_data.get('status', '')
        
        # Temel bilgileri al
        product.name = product_data.get('title', 'Printify Ürünü')
        product.description = product_data.get('description', '')
        
        # Fiyat hesapla
        variants = product_data.get('variants', [])
        if variants:
            # İlk variant'ın fiyatını al
            first_variant = variants[0]
            price_usd = Decimal(str(first_variant.get('price', 0))) / 100  # Printify cent olarak döner
            
            # TL'ye çevir
            usd_rate = self.settings.usd_to_try_rate or Decimal('34.50')
            price_try = price_usd * usd_rate
            
            # Kar marjı ekle
            profit_margin = self.settings.default_profit_margin or Decimal('30.00')
            final_price = price_try * (1 + profit_margin / 100)
            
            product.price_usd = price_usd
            product.price = final_price.quantize(Decimal('0.01'))
        
        # Stok durumu
        product.stock_status = 'in_stock'  # Printify print-on-demand
        product.stock_quantity = 999  # Sınırsız
        
        # Resim
        images = product_data.get('images', [])
        if images:
            product.image = images[0].get('src', '')
        
        # Meta bilgiler
        product.printify_last_sync = django_timezone.now()
        product.printify_data = product_data
        
        # Kategoriye göre otomatik aktif etme
        if hasattr(category, 'printify_auto_activate'):
            product.is_active = category.printify_auto_activate
        else:
            product.is_active = self.settings.auto_publish_products
        
        product.save()
        return product
    
    def _update_product_from_printify(self, product, product_data):
        """Mevcut ürünü Printify verisinden güncelle"""
        product.name = product_data.get('title', product.name)
        product.description = product_data.get('description', product.description)
        product.printify_status = product_data.get('status', product.printify_status)
        
        # Fiyat güncelle (eğer otomatik güncelleme açıksa)
        if self.settings.auto_update_prices:
            variants = product_data.get('variants', [])
            if variants:
                first_variant = variants[0]
                price_usd = Decimal(str(first_variant.get('price', 0))) / 100
                
                usd_rate = self.settings.usd_to_try_rate or Decimal('34.50')
                price_try = price_usd * usd_rate
                
                profit_margin = self.settings.default_profit_margin or Decimal('30.00')
                final_price = price_try * (1 + profit_margin / 100)
                
                product.price_usd = price_usd
                product.price = final_price.quantize(Decimal('0.01'))
        
        # Resim güncelle
        images = product_data.get('images', [])
        if images and not product.image:
            product.image = images[0].get('src', '')
        
        product.printify_last_sync = django_timezone.now()
        product.printify_data = product_data
        product.save()
        
        return product
    
    def create_printify_order(self, order_data):
        """Printify'da sipariş oluştur"""
        if not self.settings.shop_id:
            raise Exception("Printify Shop ID tanımlanmamış")
        
        return self.api.create_order(self.settings.shop_id, order_data)
    
    def get_product_mockup_url(self, product_id, variant_id=None):
        """Ürün mockup URL'si oluştur"""
        if not product_id:
            return None
        
        # Printify mockup URL formatı
        base_url = "https://printify.com/app/products"
        return f"{base_url}/{product_id}"