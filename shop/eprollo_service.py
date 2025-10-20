"""
EPROLO API Integration Service - Full Featured

Official Documentation: https://www.eprolo.com/document/
API Endpoint: https://api-b2b.eprolo.com

Features:
- Product search & listing
- Product details & variants
- Inventory management
- Order creation & tracking
- Shipping calculation
- Warehouse management
"""

import requests
import hashlib
import time
import json
import os
from decimal import Decimal
from typing import Dict, List, Optional, Any


class EprolloAPIService:
    """EPROLO API Integration - Complete Implementation"""
    
    def __init__(self, api_key=None, api_secret=None, use_mock=None):
        """
        Initialize EPROLO API Service
        
        Args:
            api_key: EPROLO API Key (from .env or settings)
            api_secret: EPROLO API Secret
            use_mock: Use mock responses for testing
        """
        # Load from environment or use provided values
        self.api_key = api_key or os.getenv('EPROLO_API_KEY', 'TEST_8888888_Key')
        self.api_secret = api_secret or os.getenv('EPROLO_API_SECRET', 'TEST_8888888_Secret')
        self.use_mock = use_mock if use_mock is not None else os.getenv('EPROLO_USE_MOCK', 'True').lower() == 'true'
        self.base_url = os.getenv('EPROLO_BASE_URL', 'https://api-b2b.eprolo.com')
        self.usd_to_try_rate = Decimal(os.getenv('USD_TO_TRY_RATE', '34.50'))
    
    def _generate_signature(self, params: Dict) -> str:
        """
        Generate API signature for EPROLO authentication
        
        EPROLO uses MD5 hash of sorted parameters + API secret
        """
        # Sort parameters alphabetically
        sorted_params = sorted(params.items())
        
        # Create signature string: key1=val1&key2=val2&...&secret
        sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_string += self.api_secret
        
        # Generate MD5 hash (uppercase)
        signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        return signature
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make authenticated API request to EPROLO
        
        Args:
            endpoint: API endpoint (e.g., 'open/product/list')
            method: HTTP method (GET or POST)
            data: Request parameters
            
        Returns:
            API response as dictionary
        """
        
        # Mock response for testing
        if self.use_mock:
            return self._mock_response(endpoint, method, data)
        
        url = f"{self.base_url}/{endpoint}"
        
        # Add timestamp and API key to parameters
        if data is None:
            data = {}
        
        data['appKey'] = self.api_key
        data['timestamp'] = str(int(time.time() * 1000))  # milliseconds
        
        # Generate signature
        data['sign'] = self._generate_signature(data)
        
        # Headers
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, params=data, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            # EPROLO response format: {code: 0, msg: "success", data: {...}}
            if result.get('code') == 0:
                result['success'] = True
            else:
                result['success'] = False
                result['error'] = result.get('msg', 'Unknown error')
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'code': -1,
                'error': str(e),
                'msg': f'Request failed: {str(e)}',
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def _mock_response(self, endpoint: str, method: str, data: Optional[Dict]) -> Dict[str, Any]:
        """
        Generate realistic mock responses for testing
        Simulates EPROLO API responses without real API calls
        """
        
        # ========== PRODUCT ENDPOINTS ==========
        
        # Product Search
        if 'product/search' in endpoint:
            keyword = data.get('keyword', '') if data else ''
            page = data.get('page', 1) if data else 1
            pageSize = data.get('pageSize', 20) if data else 20
            
            return {
                'success': True,
                'code': 0,
                'msg': 'success',
                'data': {
                    'list': [
                        {
                            'productId': '1001',
                            'name': f'Premium {keyword} T-Shirt' if keyword else 'Premium Cotton T-Shirt',
                            'price': 29.99,
                            'compareAtPrice': 49.99,
                            'currency': 'USD',
                            'mainImage': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500',
                            'stock': 150,
                            'category': 'Clothing'
                        },
                        {
                            'productId': '1002',
                            'name': 'Cozy Winter Hoodie',
                            'price': 59.99,
                            'compareAtPrice': 89.99,
                            'currency': 'USD',
                            'mainImage': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500',
                            'stock': 80,
                            'category': 'Clothing'
                        }
                    ],
                    'total': 45,
                    'page': page,
                    'pageSize': pageSize
                }
            }
        
        # Product List
        elif 'product/list' in endpoint:
            page = data.get('page', 1) if data else 1
            pageSize = data.get('pageSize', 20) if data else 20
            
            products = [
                {
                    'productId': '1001',
                    'name': 'Premium Cotton T-Shirt',
                    'price': 29.99,
                    'compareAtPrice': 49.99,
                    'currency': 'USD',
                    'mainImage': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500',
                    'stock': 150,
                    'category': 'Clothing',
                    'tags': ['bestseller', 'eco-friendly']
                },
                {
                    'productId': '1002',
                    'name': 'Cozy Winter Hoodie',
                    'price': 59.99,
                    'compareAtPrice': 89.99,
                    'currency': 'USD',
                    'mainImage': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500',
                    'stock': 80,
                    'category': 'Clothing',
                    'tags': ['winter', 'warm']
                },
                {
                    'productId': '1003',
                    'name': 'Ceramic Coffee Mug',
                    'price': 14.99,
                    'compareAtPrice': 24.99,
                    'currency': 'USD',
                    'mainImage': 'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=500',
                    'stock': 200,
                    'category': 'Home & Kitchen',
                    'tags': ['gift', 'handmade']
                },
                {
                    'productId': '1004',
                    'name': 'Canvas Tote Bag',
                    'price': 24.99,
                    'compareAtPrice': 39.99,
                    'currency': 'USD',
                    'mainImage': 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=500',
                    'stock': 120,
                    'category': 'Accessories',
                    'tags': ['eco', 'reusable']
                },
                {
                    'productId': '1005',
                    'name': 'Wireless Earbuds Pro',
                    'price': 79.99,
                    'compareAtPrice': 129.99,
                    'currency': 'USD',
                    'mainImage': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500',
                    'stock': 60,
                    'category': 'Electronics',
                    'tags': ['tech', 'bluetooth']
                },
                {
                    'productId': '1006',
                    'name': 'Yoga Mat Premium',
                    'price': 34.99,
                    'compareAtPrice': 54.99,
                    'currency': 'USD',
                    'mainImage': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500',
                    'stock': 90,
                    'category': 'Sports',
                    'tags': ['fitness', 'yoga']
                }
            ]
            
            return {
                'success': True,
                'code': 0,
                'msg': 'success',
                'data': {
                    'list': products[:pageSize],
                    'total': 156,
                    'page': page,
                    'pageSize': pageSize
                }
            }
        
        # Product Detail
        elif 'product/detail' in endpoint:
            product_id = data.get('productId', '1001') if data else '1001'
            
            product_details = {
                '1001': {
                    'productId': '1001',
                    'name': 'Premium Cotton T-Shirt',
                    'description': '''Premium quality 100% organic cotton t-shirt. 
                    Perfect for everyday wear. Available in multiple sizes and colors.
                    Features: Breathable, Durable, Eco-friendly, Pre-shrunk.''',
                    'price': 29.99,
                    'compareAtPrice': 49.99,
                    'currency': 'USD',
                    'weight': 0.2,
                    'weightUnit': 'kg',
                    'mainImage': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800',
                    'images': [
                        'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800',
                        'https://images.unsplash.com/photo-1503341455253-b2e723bb3dbb?w=800',
                        'https://images.unsplash.com/photo-1562157873-818bc0726f68?w=800'
                    ],
                    'stock': 150,
                    'category': 'Clothing',
                    'tags': ['bestseller', 'eco-friendly', 'cotton'],
                    'variants': [
                        {'variantId': '1001-S-BLK', 'size': 'S', 'color': 'Black', 'stock': 50, 'price': 29.99},
                        {'variantId': '1001-M-BLK', 'size': 'M', 'color': 'Black', 'stock': 60, 'price': 29.99},
                        {'variantId': '1001-L-BLK', 'size': 'L', 'color': 'Black', 'stock': 40, 'price': 29.99},
                        {'variantId': '1001-S-WHT', 'size': 'S', 'color': 'White', 'stock': 45, 'price': 29.99}
                    ],
                    'shipping': {
                        'freeShippingOver': 50,
                        'processingDays': '1-3',
                        'countries': ['TR', 'US', 'GB', 'DE']
                    }
                },
                '1002': {
                    'productId': '1002',
                    'name': 'Cozy Winter Hoodie',
                    'description': '''Warm and comfortable hoodie for cold weather.
                    Made with premium fleece material. Perfect for outdoor activities.''',
                    'price': 59.99,
                    'compareAtPrice': 89.99,
                    'currency': 'USD',
                    'weight': 0.5,
                    'weightUnit': 'kg',
                    'mainImage': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800',
                    'images': [
                        'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800',
                        'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800'
                    ],
                    'stock': 80,
                    'category': 'Clothing',
                    'variants': [
                        {'variantId': '1002-M', 'size': 'M', 'stock': 30, 'price': 59.99},
                        {'variantId': '1002-L', 'size': 'L', 'stock': 35, 'price': 59.99},
                        {'variantId': '1002-XL', 'size': 'XL', 'stock': 15, 'price': 59.99}
                    ]
                }
            }
            
            product = product_details.get(product_id, product_details['1001'])
            
            return {
                'success': True,
                'code': 0,
                'msg': 'success',
                'data': product
            }
        
        # Product Variants
        elif 'product/variant' in endpoint:
            product_id = data.get('productId', '1001') if data else '1001'
            
            return {
                'success': True,
                'code': 0,
                'msg': 'success',
                'data': {
                    'variants': [
                        {
                            'variantId': f'{product_id}-S-BLK',
                            'sku': f'SKU-{product_id}-S-BLK',
                            'attributes': {'size': 'S', 'color': 'Black'},
                            'price': 29.99,
                            'stock': 50,
                            'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300'
                        },
                        {
                            'variantId': f'{product_id}-M-BLK',
                            'sku': f'SKU-{product_id}-M-BLK',
                            'attributes': {'size': 'M', 'color': 'Black'},
                            'price': 29.99,
                            'stock': 60,
                            'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300'
                        }
                    ]
                }
            }
        
        # Product Inventory
        elif 'product/inventory' in endpoint:
            return {
                'success': True,
                'code': 0,
                'msg': 'success',
                'data': {
                    'productId': data.get('productId') if data else '1001',
                    'totalStock': 150,
                    'availableStock': 145,
                    'reservedStock': 5,
                    'warehouseStock': [
                        {'warehouseId': 'US-WEST', 'stock': 80},
                        {'warehouseId': 'EU-CENTRAL', 'stock': 65},
                        {'warehouseId': 'ASIA-EAST', 'stock': 5}
                    ]
                }
            }
        
        # ========== ORDER ENDPOINTS ==========
        
        # Create Order
        elif 'order/create' in endpoint:
            return {
                'success': True,
                'code': 0,
                'msg': 'Order created successfully',
                'data': {
                    'orderId': f'EPR{int(time.time())}',
                    'orderNo': f'EPR20250118{int(time.time() % 10000):04d}',
                    'status': 'pending',
                    'totalAmount': 59.98,
                    'shippingCost': 8.99,
                    'grandTotal': 68.97,
                    'currency': 'USD',
                    'createdAt': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'estimatedShipping': '2025-01-25'
                }
            }
        
        # Order Detail
        elif 'order/detail' in endpoint:
            order_id = data.get('orderId', 'EPR123456') if data else 'EPR123456'
            
            return {
                'success': True,
                'code': 0,
                'msg': 'success',
                'data': {
                    'orderId': order_id,
                    'orderNo': f'{order_id[:3]}20250118001',
                    'status': 'processing',
                    'statusText': 'İşleniyor',
                    'trackingNumber': f'TRK{order_id}',
                    'trackingUrl': f'https://tracking.example.com/{order_id}',
                    'carrier': 'DHL Express',
                    'products': [
                        {
                            'productId': '1001',
                            'productName': 'Premium Cotton T-Shirt',
                            'quantity': 2,
                            'price': 29.99
                        }
                    ],
                    'totalAmount': 59.98,
                    'shippingCost': 8.99,
                    'grandTotal': 68.97,
                    'currency': 'USD',
                    'shippingInfo': {
                        'name': 'Test Kullanıcı',
                        'phone': '+90 555 123 4567',
                        'country': 'TR',
                        'city': 'İstanbul',
                        'address': 'Test Sokak No:1'
                    },
                    'createdAt': '2025-01-18 10:30:00',
                    'estimatedDelivery': '2025-01-25'
                }
            }
        
        # Order List
        elif 'order/list' in endpoint:
            page = data.get('page', 1) if data else 1
            pageSize = data.get('pageSize', 20) if data else 20
            
            return {
                'success': True,
                'code': 0,
                'msg': 'success',
                'data': {
                    'list': [
                        {
                            'orderId': 'EPR123456',
                            'orderNo': 'EPR20250118001',
                            'status': 'shipped',
                            'totalAmount': 68.97,
                            'currency': 'USD',
                            'createdAt': '2025-01-15 10:30:00'
                        },
                        {
                            'orderId': 'EPR123457',
                            'orderNo': 'EPR20250118002',
                            'status': 'processing',
                            'totalAmount': 45.50,
                            'currency': 'USD',
                            'createdAt': '2025-01-16 14:20:00'
                        }
                    ],
                    'total': 25,
                    'page': page,
                    'pageSize': pageSize
                }
            }
        
        # Cancel Order
        elif 'order/cancel' in endpoint:
            return {
                'success': True,
                'code': 0,
                'msg': 'Order cancelled successfully',
                'data': {
                    'orderId': data.get('orderId') if data else 'EPR123456',
                    'status': 'cancelled',
                    'cancelledAt': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        
        # ========== SHIPPING ENDPOINTS ==========
        
        # Shipping Methods
        elif 'shipping/methods' in endpoint:
            return {
                'success': True,
                'code': 0,
                'msg': 'success',
                'data': [
                    {
                        'id': 'standard',
                        'name': 'Standard Shipping',
                        'name_tr': 'Standart Kargo',
                        'estimatedDays': '7-15',
                        'baseCost': 5.99,
                        'currency': 'USD'
                    },
                    {
                        'id': 'express',
                        'name': 'Express Shipping',
                        'name_tr': 'Hızlı Kargo',
                        'estimatedDays': '3-5',
                        'baseCost': 19.99,
                        'currency': 'USD'
                    },
                    {
                        'id': 'economy',
                        'name': 'Economy Shipping',
                        'name_tr': 'Ekonomik Kargo',
                        'estimatedDays': '15-30',
                        'baseCost': 2.99,
                        'currency': 'USD'
                    }
                ]
            }
        
        # Calculate Shipping
        elif 'shipping/calculate' in endpoint:
            products = data.get('products', []) if data else []
            total_weight = len(products) * 0.5  # Estimate
            
            return {
                'success': True,
                'code': 0,
                'msg': 'success',
                'data': {
                    'shippingCost': round(8.99 + (total_weight * 1.5), 2),
                    'currency': 'USD',
                    'estimatedDays': 10,
                    'method': data.get('shippingMethod', 'standard') if data else 'standard',
                    'carrier': 'DHL'
                }
            }
        
        # Tracking Info
        elif 'tracking/info' in endpoint:
            order_id = data.get('orderId', 'EPR123456') if data else 'EPR123456'
            
            return {
                'success': True,
                'code': 0,
                'msg': 'success',
                'data': {
                    'orderId': order_id,
                    'trackingNumber': f'TRK{order_id}',
                    'carrier': 'DHL Express',
                    'carrierCode': 'DHL',
                    'status': 'in_transit',
                    'statusText': 'Yolda',
                    'estimatedDelivery': '2025-01-25',
                    'trackingUrl': f'https://www.dhl.com/tr-tr/home/tracking.html?tracking-id=TRK{order_id}',
                    'events': [
                        {
                            'date': '2025-01-18 10:00:00',
                            'status': 'picked_up',
                            'location': 'İstanbul Depo',
                            'description': 'Kargo alındı'
                        },
                        {
                            'date': '2025-01-18 14:30:00',
                            'status': 'in_transit',
                            'location': 'İstanbul Transfer Merkezi',
                            'description': 'Transfer merkezine ulaştı'
                        },
                        {
                            'date': '2025-01-19 08:00:00',
                            'status': 'in_transit',
                            'location': 'Ankara Transfer Merkezi',
                            'description': 'Yolda'
                        }
                    ]
                }
            }
        
        # ========== WAREHOUSE ENDPOINTS ==========
        
        # Warehouse List
        elif 'warehouse/list' in endpoint:
            return {
                'success': True,
                'code': 0,
                'msg': 'success',
                'data': [
                    {
                        'warehouseId': 'US-WEST',
                        'name': 'US West Coast Warehouse',
                        'location': 'Los Angeles, CA',
                        'country': 'US',
                        'capabilities': ['fulfillment', 'storage', 'returns']
                    },
                    {
                        'warehouseId': 'EU-CENTRAL',
                        'name': 'EU Central Warehouse',
                        'location': 'Frankfurt, Germany',
                        'country': 'DE',
                        'capabilities': ['fulfillment', 'storage']
                    },
                    {
                        'warehouseId': 'ASIA-EAST',
                        'name': 'Asia East Warehouse',
                        'location': 'Shanghai, China',
                        'country': 'CN',
                        'capabilities': ['manufacturing', 'fulfillment', 'storage']
                    }
                ]
            }
        
        # Warehouse Inventory
        elif 'warehouse/inventory' in endpoint:
            return {
                'success': True,
                'code': 0,
                'msg': 'success',
                'data': {
                    'warehouseId': data.get('warehouseId', 'US-WEST') if data else 'US-WEST',
                    'productId': data.get('productId', '1001') if data else '1001',
                    'stock': 80,
                    'availableStock': 75,
                    'reservedStock': 5,
                    'lastUpdated': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        
        # Unknown endpoint
        return {
            'success': False,
            'code': 404,
            'msg': f'Mock endpoint not found: {endpoint}',
            'data': None
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test API connection"""
        return self.get_products(page=1, pageSize=1)
    
    # ==================== PRODUCT METHODS ====================
    
    def search_products(self, keyword: str, page: int = 1, pageSize: int = 20) -> Dict[str, Any]:
        """
        Search products by keyword
        
        Args:
            keyword: Search term (product name, SKU, etc.)
            page: Page number (default 1)
            pageSize: Items per page (default 20, max 100)
            
        Returns:
            {
                'success': True/False,
                'data': {
                    'list': [...products...],
                    'total': 150,
                    'page': 1,
                    'pageSize': 20
                }
            }
        """
        data = {
            'keyword': keyword,
            'page': page,
            'pageSize': min(pageSize, 100)
        }
        return self._make_request('open/product/search', method='POST', data=data)
    
    def get_products(self, category: Optional[str] = None, page: int = 1, pageSize: int = 20) -> Dict[str, Any]:
        """
        Get product list
        
        Args:
            category: Category filter (optional)
            page: Page number
            pageSize: Items per page (max 100)
            
        Returns:
            Product list response
        """
        data = {
            'page': page,
            'pageSize': min(pageSize, 100)
        }
        if category:
            data['category'] = category
        
        return self._make_request('open/product/list', method='POST', data=data)
    
    def get_product_detail(self, product_id: str) -> Dict[str, Any]:
        """
        Get detailed product information
        
        Args:
            product_id: EPROLO product ID
            
        Returns:
            {
                'success': True/False,
                'data': {
                    'id': '123',
                    'name': 'Product Name',
                    'description': '...',
                    'price': 29.99,
                    'currency': 'USD',
                    'stock': 100,
                    'images': [...],
                    'variants': [...],
                    'shipping_info': {...}
                }
            }
        """
        data = {'productId': product_id}
        return self._make_request('open/product/detail', method='POST', data=data)
    
    def get_product_variants(self, product_id: str) -> Dict[str, Any]:
        """
        Get product variants (size, color, etc.)
        
        Args:
            product_id: EPROLO product ID
            
        Returns:
            Variant list with prices and stock
        """
        data = {'productId': product_id}
        return self._make_request('open/product/variant/list', method='POST', data=data)
    
    def get_product_inventory(self, product_id: str, variant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check product inventory/stock
        
        Args:
            product_id: EPROLO product ID
            variant_id: Specific variant ID (optional)
            
        Returns:
            Stock information
        """
        data = {'productId': product_id}
        if variant_id:
            data['variantId'] = variant_id
        
        return self._make_request('open/product/inventory', method='POST', data=data)
    
    # ==================== ORDER METHODS ====================
    
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create order on EPROLO
        
        Args:
            order_data: {
                'products': [
                    {
                        'productId': '123',
                        'variantId': '456',  # optional
                        'quantity': 2,
                        'price': 29.99  # your selling price
                    }
                ],
                'shippingInfo': {
                    'firstName': 'Ahmet',
                    'lastName': 'Yılmaz',
                    'phone': '+90 555 123 4567',
                    'email': 'ahmet@example.com',
                    'country': 'TR',
                    'province': 'İstanbul',
                    'city': 'Kadıköy',
                    'address': 'Moda Cad. No:123',
                    'postalCode': '34710'
                },
                'shippingMethod': 'standard',  # standard, express, economy
                'remark': 'Optional order note'
            }
            
        Returns:
            {
                'success': True/False,
                'data': {
                    'orderId': 'EPR-123456',
                    'orderNo': 'EPR20250118001',
                    'status': 'pending',
                    'totalAmount': 59.98,
                    'shippingCost': 5.99,
                    'grandTotal': 65.97
                }
            }
        """
        return self._make_request('open/order/create', method='POST', data=order_data)
    
    def get_order_detail(self, order_id: str) -> Dict[str, Any]:
        """
        Get order details and status
        
        Args:
            order_id: EPROLO order ID
            
        Returns:
            Order details with status and tracking
        """
        data = {'orderId': order_id}
        return self._make_request('open/order/detail', method='POST', data=data)
    
    def get_order_list(self, status: Optional[str] = None, page: int = 1, pageSize: int = 20) -> Dict[str, Any]:
        """
        Get order list
        
        Args:
            status: Filter by status (pending, processing, shipped, completed, cancelled)
            page: Page number
            pageSize: Items per page
            
        Returns:
            Order list
        """
        data = {
            'page': page,
            'pageSize': min(pageSize, 100)
        }
        if status:
            data['status'] = status
        
        return self._make_request('open/order/list', method='POST', data=data)
    
    def cancel_order(self, order_id: str, reason: str = '') -> Dict[str, Any]:
        """
        Cancel an order
        
        Args:
            order_id: EPROLO order ID
            reason: Cancellation reason
            
        Returns:
            Cancellation result
        """
        data = {
            'orderId': order_id,
            'reason': reason
        }
        return self._make_request('open/order/cancel', method='POST', data=data)
    
    # ==================== SHIPPING METHODS ====================
    
    def get_shipping_methods(self, country: str = 'TR') -> Dict[str, Any]:
        """
        Get available shipping methods for country
        
        Args:
            country: Country code (TR, US, GB, etc.)
            
        Returns:
            {
                'success': True,
                'data': [
                    {
                        'id': 'standard',
                        'name': 'Standard Shipping',
                        'estimatedDays': '7-15',
                        'baseCost': 5.99
                    },
                    ...
                ]
            }
        """
        data = {'country': country}
        return self._make_request('open/shipping/methods', method='POST', data=data)
    
    def calculate_shipping(self, country: str, province: str, city: str, 
                          products: List[Dict], shipping_method: str = 'standard') -> Dict[str, Any]:
        """
        Calculate shipping cost
        
        Args:
            country: Destination country code
            province: Province/State
            city: City
            products: List of {'productId': '123', 'quantity': 2}
            shipping_method: Shipping method ID
            
        Returns:
            {
                'success': True,
                'data': {
                    'shippingCost': 8.99,
                    'currency': 'USD',
                    'estimatedDays': 10,
                    'method': 'standard'
                }
            }
        """
        data = {
            'country': country,
            'province': province,
            'city': city,
            'products': products,
            'shippingMethod': shipping_method
        }
        return self._make_request('open/shipping/calculate', method='POST', data=data)
    
    def get_tracking_info(self, order_id: str) -> Dict[str, Any]:
        """
        Get order tracking information
        
        Args:
            order_id: EPROLO order ID
            
        Returns:
            {
                'success': True,
                'data': {
                    'trackingNumber': 'TRK123456789',
                    'carrier': 'DHL',
                    'status': 'in_transit',
                    'estimatedDelivery': '2025-01-25',
                    'trackingUrl': 'https://...',
                    'events': [...]
                }
            }
        """
        data = {'orderId': order_id}
        return self._make_request('open/tracking/info', method='POST', data=data)
    
    # ==================== WAREHOUSE METHODS ====================
    
    def get_warehouses(self) -> Dict[str, Any]:
        """
        Get available EPROLO warehouses
        
        Returns:
            List of warehouses with locations and capabilities
        """
        return self._make_request('open/warehouse/list', method='POST', data={})
    
    def get_warehouse_inventory(self, warehouse_id: str, product_id: str) -> Dict[str, Any]:
        """
        Check product stock in specific warehouse
        
        Args:
            warehouse_id: Warehouse ID
            product_id: Product ID
            
        Returns:
            Stock information for warehouse
        """
        data = {
            'warehouseId': warehouse_id,
            'productId': product_id
        }
        return self._make_request('open/warehouse/inventory', method='POST', data=data)
    
    # ==================== UTILITY METHODS ====================
    
    def convert_usd_to_try(self, usd_amount: float) -> Decimal:
        """Convert USD price to Turkish Lira"""
        return Decimal(str(usd_amount)) * self.usd_to_try_rate
    
    def get_product_price_try(self, product_id: str) -> Optional[Decimal]:
        """Get product price in TRY"""
        result = self.get_product_detail(product_id)
        if result.get('success') and result.get('data'):
            usd_price = result['data'].get('price', 0)
            return self.convert_usd_to_try(usd_price)
        return None


# ==================== TEST FUNCTIONS ====================

def test_eprollo_api():
    """Comprehensive EPROLO API Test"""
    service = EprolloAPIService()
    
    print("=" * 70)
    print("🧪 EPROLO API FULL FEATURE TEST")
    print("=" * 70)
    print(f"📍 Mode: {'MOCK (Test Data)' if service.use_mock else 'REAL API'}")
    print(f"💱 USD/TRY Rate: {service.usd_to_try_rate}")
    print("=" * 70)
    
    # Test 1: Connection Test
    print("\n1️⃣  CONNECTION TEST")
    print("-" * 70)
    result = service.test_connection()
    if result.get('success'):
        print("✅ Connection successful!")
        print(f"   Total products available: {result.get('data', {}).get('total', 0)}")
    else:
        print(f"❌ Connection failed: {result.get('msg')}")
    
    # Test 2: Product Search
    print("\n2️⃣  PRODUCT SEARCH TEST")
    print("-" * 70)
    result = service.search_products(keyword='shirt', page=1, pageSize=3)
    if result.get('success'):
        products = result.get('data', {}).get('list', [])
        print(f"✅ Found {len(products)} products matching 'shirt':")
        for p in products:
            print(f"   • {p['name']} - ${p['price']} ({service.convert_usd_to_try(p['price'])} TL)")
    else:
        print(f"❌ Search failed: {result.get('msg')}")
    
    # Test 3: Get Product List
    print("\n3️⃣  PRODUCT LIST TEST")
    print("-" * 70)
    result = service.get_products(page=1, pageSize=5)
    if result.get('success'):
        products = result.get('data', {}).get('list', [])
        total = result.get('data', {}).get('total', 0)
        print(f"✅ Retrieved {len(products)} products (Total available: {total}):")
        for p in products:
            print(f"   • [{p['productId']}] {p['name']}")
            print(f"     Price: ${p['price']} → {service.convert_usd_to_try(p['price'])} TL")
            print(f"     Stock: {p.get('stock', 0)} units")
    else:
        print(f"❌ List failed: {result.get('msg')}")
    
    # Test 4: Product Detail
    print("\n4️⃣  PRODUCT DETAIL TEST")
    print("-" * 70)
    result = service.get_product_detail(product_id='1001')
    if result.get('success'):
        product = result.get('data', {})
        print(f"✅ Product Details Retrieved:")
        print(f"   Name: {product.get('name')}")
        print(f"   Description: {product.get('description', '')[:100]}...")
        print(f"   Price: ${product.get('price')} (Compare at: ${product.get('compareAtPrice')})")
        print(f"   Price TRY: {service.convert_usd_to_try(product.get('price', 0))} TL")
        print(f"   Stock: {product.get('stock')} units")
        print(f"   Images: {len(product.get('images', []))} photos")
        print(f"   Variants: {len(product.get('variants', []))} options")
    else:
        print(f"❌ Detail failed: {result.get('msg')}")
    
    # Test 5: Product Variants
    print("\n5️⃣  PRODUCT VARIANTS TEST")
    print("-" * 70)
    result = service.get_product_variants(product_id='1001')
    if result.get('success'):
        variants = result.get('data', {}).get('variants', [])
        print(f"✅ Found {len(variants)} variants:")
        for v in variants:
            attrs = v.get('attributes', {})
            print(f"   • {v['variantId']}: {attrs.get('size')} / {attrs.get('color')}")
            print(f"     Stock: {v.get('stock')}, Price: ${v.get('price')}")
    else:
        print(f"❌ Variants failed: {result.get('msg')}")
    
    # Test 6: Product Inventory
    print("\n6️⃣  INVENTORY CHECK TEST")
    print("-" * 70)
    result = service.get_product_inventory(product_id='1001')
    if result.get('success'):
        inv = result.get('data', {})
        print(f"✅ Inventory Status:")
        print(f"   Total Stock: {inv.get('totalStock')}")
        print(f"   Available: {inv.get('availableStock')}")
        print(f"   Reserved: {inv.get('reservedStock')}")
        warehouses = inv.get('warehouseStock', [])
        if warehouses:
            print(f"   Warehouses:")
            for wh in warehouses:
                print(f"     • {wh['warehouseId']}: {wh['stock']} units")
    else:
        print(f"❌ Inventory check failed: {result.get('msg')}")
    
    # Test 7: Shipping Methods
    print("\n7️⃣  SHIPPING METHODS TEST")
    print("-" * 70)
    result = service.get_shipping_methods(country='TR')
    if result.get('success'):
        methods = result.get('data', [])
        print(f"✅ Available shipping methods for Turkey:")
        for method in methods:
            print(f"   • {method['name']} ({method.get('name_tr', '')})")
            print(f"     Cost: ${method['baseCost']} → {service.convert_usd_to_try(method['baseCost'])} TL")
            print(f"     Delivery: {method['estimatedDays']} days")
    else:
        print(f"❌ Shipping methods failed: {result.get('msg')}")
    
    # Test 8: Calculate Shipping
    print("\n8️⃣  SHIPPING CALCULATION TEST")
    print("-" * 70)
    products_to_ship = [
        {'productId': '1001', 'quantity': 2},
        {'productId': '1002', 'quantity': 1}
    ]
    result = service.calculate_shipping(
        country='TR',
        province='İstanbul',
        city='Kadıköy',
        products=products_to_ship,
        shipping_method='standard'
    )
    if result.get('success'):
        shipping = result.get('data', {})
        print(f"✅ Shipping Cost Calculated:")
        print(f"   Cost: ${shipping.get('shippingCost')} → {service.convert_usd_to_try(shipping.get('shippingCost', 0))} TL")
        print(f"   Method: {shipping.get('method')}")
        print(f"   Carrier: {shipping.get('carrier')}")
        print(f"   Estimated Days: {shipping.get('estimatedDays')}")
    else:
        print(f"❌ Shipping calculation failed: {result.get('msg')}")
    
    # Test 9: Create Order
    print("\n9️⃣  ORDER CREATION TEST")
    print("-" * 70)
    order_data = {
        'products': [
            {
                'productId': '1001',
                'variantId': '1001-M-BLK',
                'quantity': 2,
                'price': 29.99
            }
        ],
        'shippingInfo': {
            'firstName': 'Ahmet',
            'lastName': 'Yılmaz',
            'phone': '+90 555 123 4567',
            'email': 'ahmet@example.com',
            'country': 'TR',
            'province': 'İstanbul',
            'city': 'Kadıköy',
            'address': 'Moda Cad. No:123 Daire:5',
            'postalCode': '34710'
        },
        'shippingMethod': 'standard',
        'remark': 'Test siparişi - Lütfen özenle paketleyin'
    }
    result = service.create_order(order_data)
    test_order_id = None
    if result.get('success'):
        order = result.get('data', {})
        test_order_id = order.get('orderId')
        print(f"✅ Order Created Successfully:")
        print(f"   Order ID: {order.get('orderId')}")
        print(f"   Order No: {order.get('orderNo')}")
        print(f"   Status: {order.get('status')}")
        print(f"   Total: ${order.get('totalAmount')} → {service.convert_usd_to_try(order.get('totalAmount', 0))} TL")
        print(f"   Shipping: ${order.get('shippingCost')} → {service.convert_usd_to_try(order.get('shippingCost', 0))} TL")
        print(f"   Grand Total: ${order.get('grandTotal')} → {service.convert_usd_to_try(order.get('grandTotal', 0))} TL")
        print(f"   Created: {order.get('createdAt')}")
    else:
        print(f"❌ Order creation failed: {result.get('msg')}")
    
    # Test 10: Get Order Detail
    if test_order_id:
        print("\n🔟 ORDER DETAIL TEST")
        print("-" * 70)
        result = service.get_order_detail(order_id=test_order_id)
        if result.get('success'):
            order = result.get('data', {})
            print(f"✅ Order Details Retrieved:")
            print(f"   Order No: {order.get('orderNo')}")
            print(f"   Status: {order.get('statusText', order.get('status'))}")
            print(f"   Tracking: {order.get('trackingNumber', 'Not yet available')}")
            print(f"   Carrier: {order.get('carrier', 'TBA')}")
            print(f"   Total: ${order.get('grandTotal')} → {service.convert_usd_to_try(order.get('grandTotal', 0))} TL")
        else:
            print(f"❌ Order detail failed: {result.get('msg')}")
    
    # Test 11: Tracking Info
    print("\n1️⃣1️⃣  TRACKING INFO TEST")
    print("-" * 70)
    result = service.get_tracking_info(order_id=test_order_id or 'EPR123456')
    if result.get('success'):
        tracking = result.get('data', {})
        print(f"✅ Tracking Information:")
        print(f"   Tracking #: {tracking.get('trackingNumber')}")
        print(f"   Carrier: {tracking.get('carrier')}")
        print(f"   Status: {tracking.get('statusText', tracking.get('status'))}")
        print(f"   Estimated Delivery: {tracking.get('estimatedDelivery')}")
        print(f"   Tracking URL: {tracking.get('trackingUrl')}")
        events = tracking.get('events', [])
        if events:
            print(f"   Recent Events:")
            for event in events[:3]:
                print(f"     • {event['date']}: {event['description']} ({event['location']})")
    else:
        print(f"❌ Tracking failed: {result.get('msg')}")
    
    # Test 12: Warehouse List
    print("\n1️⃣2️⃣  WAREHOUSE LIST TEST")
    print("-" * 70)
    result = service.get_warehouses()
    if result.get('success'):
        warehouses = result.get('data', [])
        print(f"✅ Available Warehouses ({len(warehouses)}):")
        for wh in warehouses:
            print(f"   • {wh['name']} ({wh['warehouseId']})")
            print(f"     Location: {wh['location']}, {wh['country']}")
            print(f"     Capabilities: {', '.join(wh['capabilities'])}")
    else:
        print(f"❌ Warehouse list failed: {result.get('msg')}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 70)
    print(f"\n💡 TIP: Set EPROLO_USE_MOCK=False in .env to use real API")
    print(f"🔑 Get your API credentials from: https://www.eprolo.com/developer")
    print("=" * 70)


if __name__ == '__main__':
    test_eprollo_api()
