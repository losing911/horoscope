"""
EPROLO API Entegrasyon Servisi
- Kategori bazlı ürün senkronizasyonu
- Stok ve fiyat güncelleme
- Sipariş gönderimi
"""

import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.db import transaction
from .models import Product, Category, EproloSettings, EproloSyncLog


class EproloAPIError(Exception):
    """EPROLO API hatası"""
    pass


class EproloService:
    """EPROLO API ile kategori bazlı entegrasyon servisi"""
    
    def __init__(self):
        self.settings = self._get_settings()
        self.base_url = "https://api.eprolo.com/v1"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.settings.api_key}'
        }
    
    def _get_settings(self) -> EproloSettings:
        """EPROLO ayarlarını getir"""
        settings, created = EproloSettings.objects.get_or_create(pk=1)
        if created or not settings.api_key:
            raise EproloAPIError("EPROLO API ayarları yapılmamış. Lütfen ayarları tamamlayın.")
        return settings
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """API isteği yap"""
        if self.settings.use_mock:
            return self._mock_api_response(endpoint, data)
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=data, timeout=30)
            else:
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise EproloAPIError(f"API isteği başarısız: {str(e)}")
    
    def _mock_api_response(self, endpoint: str, data: dict = None) -> dict:
        """Test için mock API yanıtı"""
        if 'products' in endpoint:
            return {
                'code': 200,
                'message': 'Success',
                'data': {
                    'products': [
                        {
                            'product_id': f'EP{i:06d}',
                            'title': f'Test Ürün {i}',
                            'description': f'Test ürün açıklaması {i}',
                            'price': 10.99 + i,
                            'cost_price': 5.99 + i,
                            'stock': 100,
                            'sku': f'SKU{i:05d}',
                            'images': ['https://via.placeholder.com/500'],
                            'category': data.get('category', 'Electronics') if data else 'Electronics',
                            'supplier': 'EPROLO',
                            'warehouse': 'US',
                            'variants': []
                        }
                        for i in range(1, 11)
                    ],
                    'total': 10,
                    'page': 1,
                    'per_page': 10
                }
            }
        elif 'stock' in endpoint:
            return {
                'code': 200,
                'message': 'Success',
                'data': {
                    'updates': [
                        {'sku': 'SKU001', 'stock': 95, 'updated': True}
                    ]
                }
            }
        return {'code': 200, 'message': 'Success', 'data': {}}
    
    def sync_products_by_category(self, category_id: int, page: int = 1, per_page: int = 50) -> Dict:
        """
        Kategori bazlı ürün senkronizasyonu
        
        Args:
            category_id: Senkronize edilecek kategori ID
            page: Sayfa numarası
            per_page: Sayfa başına ürün sayısı
        
        Returns:
            Senkronizasyon sonucu
        """
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise EproloAPIError(f"Kategori bulunamadı: {category_id}")
        
        # Log başlat
        sync_log = EproloSyncLog.objects.create(
            sync_type='product_import',
            status='success',
            message=f'Kategori: {category.name}'
        )
        
        try:
            # EPROLO'dan kategoriye ait ürünleri çek
            response = self._make_request('GET', 'products/list', {
                'category': category.eprolo_category_id or category.name,
                'page': page,
                'per_page': per_page
            })
            
            if response.get('code') != 200:
                raise EproloAPIError(response.get('message', 'API hatası'))
            
            products_data = response.get('data', {}).get('products', [])
            total_count = len(products_data)
            success_count = 0
            failed_count = 0
            
            # Her ürünü senkronize et
            for product_data in products_data:
                try:
                    product = self._sync_single_product(product_data, category)
                    sync_log.affected_products.add(product)
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"Ürün senkronizasyon hatası: {str(e)}")
            
            # Log güncelle
            sync_log.status = 'success' if failed_count == 0 else 'partial'
            sync_log.total_items = total_count
            sync_log.successful_items = success_count
            sync_log.failed_items = failed_count
            sync_log.completed_at = timezone.now()
            sync_log.duration_seconds = (sync_log.completed_at - sync_log.started_at).seconds
            sync_log.save()
            
            # Settings güncelle
            self.settings.last_product_sync = timezone.now()
            self.settings.save()
            
            return {
                'success': True,
                'category': category.name,
                'total': total_count,
                'success': success_count,
                'failed': failed_count,
                'log_id': sync_log.id
            }
        
        except Exception as e:
            sync_log.status = 'failed'
            sync_log.error_details = str(e)
            sync_log.completed_at = timezone.now()
            sync_log.save()
            raise
    
    def _sync_single_product(self, product_data: dict, category: Category) -> Product:
        """Tek bir ürünü senkronize et"""
        eprolo_id = product_data['product_id']
        
        # Ürünü bul veya oluştur
        product, created = Product.objects.get_or_create(
            eprolo_product_id=eprolo_id,
            defaults={
                'name': product_data['title'],
                'source': 'eprolo',
                'category': category,
                'is_active': False  # Manuel onay için pasif başlat
            }
        )
        
        # Fiyat hesapla (USD -> TRY + kar marjı)
        cost_usd = Decimal(str(product_data.get('cost_price', product_data['price'])))
        cost_try = cost_usd * self.settings.usd_to_try_rate
        profit_margin = product.profit_margin or self.settings.default_profit_margin
        price_try = cost_try * (1 + profit_margin / 100)
        
        # Ürün bilgilerini güncelle
        product.name = product_data['title']
        product.description = product_data.get('description', '')
        product.category = category
        product.price = price_try.quantize(Decimal('0.01'))
        product.cost_price = cost_try.quantize(Decimal('0.01'))
        product.stock = product_data.get('stock', 0)
        product.eprolo_sku = product_data.get('sku', '')
        product.eprolo_supplier = product_data.get('supplier', 'EPROLO')
        product.eprolo_warehouse = product_data.get('warehouse', 'US')
        product.eprolo_last_sync = timezone.now()
        
        # EPROLO data
        product.eprolo_data = {
            'raw_data': product_data,
            'images': product_data.get('images', []),
            'variants': product_data.get('variants', []),
            'synced_at': timezone.now().isoformat()
        }
        
        # İlk resmi ana resim yap
        if product_data.get('images'):
            product.image = product_data['images'][0]
        
        product.save()
        
        return product
    
    def sync_all_categories(self, auto_activate: bool = False) -> Dict:
        """Tüm kategorilerdeki EPROLO ürünlerini senkronize et"""
        
        # Sadece EPROLO entegrasyonu olan kategoriler
        categories = Category.objects.filter(
            is_active=True,
            enable_eprolo_sync=True
        )
        
        if not categories.exists():
            return {
                'success': False,
                'message': 'EPROLO senkronizasyonu aktif kategori bulunamadı'
            }
        
        results = {
            'total_categories': categories.count(),
            'categories': [],
            'total_products': 0,
            'total_success': 0,
            'total_failed': 0
        }
        
        for category in categories:
            try:
                result = self.sync_products_by_category(category.id)
                results['categories'].append(result)
                results['total_products'] += result['total']
                results['total_success'] += result['success']
                results['total_failed'] += result['failed']
            except Exception as e:
                results['categories'].append({
                    'category': category.name,
                    'error': str(e)
                })
        
        return results
    
    def update_stock_by_category(self, category_id: int) -> Dict:
        """Kategoriye ait ürünlerin stoklarını güncelle"""
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise EproloAPIError(f"Kategori bulunamadı: {category_id}")
        
        # Log başlat
        sync_log = EproloSyncLog.objects.create(
            sync_type='stock_update',
            status='success',
            message=f'Kategori: {category.name}'
        )
        
        try:
            # Kategorideki EPROLO ürünlerini al
            products = Product.objects.filter(
                category=category,
                source='eprolo',
                eprolo_product_id__isnull=False
            )
            
            if not products.exists():
                raise EproloAPIError(f"Bu kategoride EPROLO ürünü yok: {category.name}")
            
            # EPROLO'dan stok bilgilerini çek
            product_ids = list(products.values_list('eprolo_product_id', flat=True))
            
            response = self._make_request('POST', 'products/stock', {
                'product_ids': product_ids
            })
            
            if response.get('code') != 200:
                raise EproloAPIError(response.get('message', 'API hatası'))
            
            stock_data = response.get('data', {}).get('updates', [])
            success_count = 0
            failed_count = 0
            
            # Stok güncelle
            for stock_info in stock_data:
                try:
                    product = products.get(eprolo_sku=stock_info['sku'])
                    product.stock = stock_info['stock']
                    product.eprolo_last_sync = timezone.now()
                    product.save(update_fields=['stock', 'eprolo_last_sync'])
                    sync_log.affected_products.add(product)
                    success_count += 1
                except Product.DoesNotExist:
                    failed_count += 1
            
            # Log güncelle
            sync_log.status = 'success'
            sync_log.total_items = len(stock_data)
            sync_log.successful_items = success_count
            sync_log.failed_items = failed_count
            sync_log.completed_at = timezone.now()
            sync_log.duration_seconds = (sync_log.completed_at - sync_log.started_at).seconds
            sync_log.save()
            
            # Settings güncelle
            self.settings.last_stock_sync = timezone.now()
            self.settings.save()
            
            return {
                'success': True,
                'category': category.name,
                'total': len(stock_data),
                'success': success_count,
                'failed': failed_count,
                'log_id': sync_log.id
            }
        
        except Exception as e:
            sync_log.status = 'failed'
            sync_log.error_details = str(e)
            sync_log.completed_at = timezone.now()
            sync_log.save()
            raise
    
    def update_prices_by_category(self, category_id: int, new_margin: Optional[int] = None) -> Dict:
        """
        Kategoriye ait ürünlerin fiyatlarını güncelle
        
        Args:
            category_id: Kategori ID
            new_margin: Yeni kar marjı (opsiyonel)
        """
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise EproloAPIError(f"Kategori bulunamadı: {category_id}")
        
        # Log başlat
        sync_log = EproloSyncLog.objects.create(
            sync_type='price_update',
            status='success',
            message=f'Kategori: {category.name}, Yeni marj: {new_margin}%' if new_margin else f'Kategori: {category.name}'
        )
        
        try:
            # Kategorideki EPROLO ürünlerini al
            products = Product.objects.filter(
                category=category,
                source='eprolo',
                cost_price__isnull=False
            )
            
            if not products.exists():
                raise EproloAPIError(f"Bu kategoride EPROLO ürünü yok: {category.name}")
            
            success_count = 0
            
            for product in products:
                try:
                    # Yeni marj belirlenmişse kullan
                    if new_margin is not None:
                        product.profit_margin = new_margin
                    
                    # Mevcut maliyet üzerinden yeni fiyat hesapla
                    margin = product.profit_margin or self.settings.default_profit_margin
                    new_price = product.cost_price * (1 + margin / 100)
                    
                    product.price = new_price.quantize(Decimal('0.01'))
                    product.save(update_fields=['price', 'profit_margin'])
                    
                    sync_log.affected_products.add(product)
                    success_count += 1
                
                except Exception as e:
                    print(f"Fiyat güncelleme hatası ({product.name}): {str(e)}")
            
            # Log güncelle
            sync_log.status = 'success'
            sync_log.total_items = products.count()
            sync_log.successful_items = success_count
            sync_log.completed_at = timezone.now()
            sync_log.duration_seconds = (sync_log.completed_at - sync_log.started_at).seconds
            sync_log.save()
            
            # Settings güncelle
            self.settings.last_price_sync = timezone.now()
            self.settings.save()
            
            return {
                'success': True,
                'category': category.name,
                'total': products.count(),
                'success': success_count,
                'log_id': sync_log.id
            }
        
        except Exception as e:
            sync_log.status = 'failed'
            sync_log.error_details = str(e)
            sync_log.completed_at = timezone.now()
            sync_log.save()
            raise
    
    def get_category_sync_status(self, category_id: int) -> Dict:
        """Kategorinin senkronizasyon durumunu getir"""
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise EproloAPIError(f"Kategori bulunamadı: {category_id}")
        
        # Kategorideki EPROLO ürünleri
        products = Product.objects.filter(
            category=category,
            source='eprolo'
        )
        
        # Son senkronizasyonlar
        recent_logs = EproloSyncLog.objects.filter(
            details__contains=category.name
        ).order_by('-started_at')[:5]
        
        return {
            'category': category.name,
            'total_products': products.count(),
            'active_products': products.filter(is_active=True).count(),
            'total_stock': products.aggregate(total=sum('stock'))['total'] or 0,
            'low_stock_count': products.filter(stock__lt=self.settings.low_stock_threshold).count(),
            'last_sync': recent_logs.first().started_at if recent_logs.exists() else None,
            'recent_logs': [
                {
                    'type': log.sync_type,
                    'status': log.status,
                    'date': log.started_at,
                    'success_rate': log.success_rate
                }
                for log in recent_logs
            ]
        }
