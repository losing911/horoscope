"""
Eprollo API Integration Service
Test API Credentials:
- API Key: TEST_8888888_Key
- API Secret: TEST_8888888_Secret
- Content-Type: application/json
"""

import requests
import hashlib
import time
import json
# from django.conf import settings  # Not needed for standalone testing


class EprolloAPIService:
    """Eprollo API Integration"""
    
    # Test Credentials (from user)
    API_KEY = "TEST_8888888_Key"
    API_SECRET = "TEST_8888888_Secret"
    # Mock endpoint for testing
    BASE_URL = "https://httpbin.org"
    USE_MOCK = True  # Using mock mode with test credentials
    
    def __init__(self, api_key=None, api_secret=None, use_mock=None):
        """Initialize with credentials"""
        self.api_key = api_key or self.API_KEY
        self.api_secret = api_secret or self.API_SECRET
        self.use_mock = use_mock if use_mock is not None else self.USE_MOCK
    
    def _generate_signature(self, params):
        """Generate API signature for authentication"""
        # Sort parameters
        sorted_params = sorted(params.items())
        
        # Create signature string
        sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_string += self.api_secret
        
        # Generate MD5 hash
        signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        return signature
    
    def _make_request(self, endpoint, method='GET', data=None):
        """Make API request with authentication"""
        
        # Mock response for testing
        if self.use_mock:
            return self._mock_response(endpoint, method, data)
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        # EPROLO uses token-based authentication
        # Headers with Bearer token
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        # For GET requests, data goes to params
        params = data if method == 'GET' and data else None
        json_data = data if method == 'POST' and data else None
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=json_data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def _mock_response(self, endpoint, method, data):
        """Generate mock responses for testing"""
        
        # Check for product endpoint (both api/v1/products and api/v1/product/123)
        if 'product' in endpoint and method == 'GET':
            # Product detail - api/v1/product/123
            if endpoint.count('/') >= 3 and not endpoint.endswith('products'):
                product_id = endpoint.split('/')[-1]
                
                # Gerçekçi ürün görselleri
                product_images = {
                    '1001': [
                        'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800',
                        'https://images.unsplash.com/photo-1503341455253-b2e723bb3dbb?w=800',
                        'https://images.unsplash.com/photo-1562157873-818bc0726f68?w=800'
                    ],
                    '1002': [
                        'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=800',
                        'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800',
                        'https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=800'
                    ],
                    '1003': [
                        'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=800',
                        'https://images.unsplash.com/photo-1523217582562-09d0def993a6?w=800',
                        'https://images.unsplash.com/photo-1572119865084-43c285814d63?w=800'
                    ],
                    '1004': [
                        'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=800',
                        'https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=800',
                        'https://images.unsplash.com/photo-1627916607164-7b20241db935?w=800'
                    ],
                    '1005': [
                        'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800',
                        'https://images.unsplash.com/photo-1606400082777-ef05f3c5cde2?w=800',
                        'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800'
                    ]
                }
                
                images = product_images.get(product_id, ['https://via.placeholder.com/800'])
                
                return {
                    'success': True,
                    'code': 0,
                    'data': {
                        'id': product_id,
                        'name': f'Test Product {product_id}',
                        'description': 'This is a test product from EPROLO API',
                        'price': 99.99,
                        'currency': 'USD',
                        'stock': 50,
                        'images': images,
                        'category': 'test_category',
                        'variants': []
                    }
                }
            # Product list - api/v1/products
            else:
                page = data.get('page', 1) if data else 1
                pageSize = data.get('pageSize', 20) if data else 20
                return {
                    'success': True,
                    'code': 0,
                    'data': {
                        'list': [
                            {
                                'id': '1001',
                                'name': 'Premium Cotton T-Shirt',
                                'price': 29.99,
                                'currency': 'USD',
                                'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500'
                            },
                            {
                                'id': '1002',
                                'name': 'Cozy Winter Hoodie',
                                'price': 59.99,
                                'currency': 'USD',
                                'image': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500'
                            },
                            {
                                'id': '1003',
                                'name': 'Ceramic Coffee Mug',
                                'price': 14.99,
                                'currency': 'USD',
                                'image': 'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=500'
                            },
                            {
                                'id': '1004',
                                'name': 'Canvas Tote Bag',
                                'price': 24.99,
                                'currency': 'USD',
                                'image': 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=500'
                            },
                            {
                                'id': '1005',
                                'name': 'Wireless Earbuds',
                                'price': 79.99,
                                'currency': 'USD',
                                'image': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500'
                            }
                        ],
                        'total': 150,
                        'page': page,
                        'pageSize': pageSize
                    }
                }
        
        # Order creation - api/v1/order
        elif 'order' in endpoint and method == 'POST':
            return {
                'success': True,
                'code': 0,
                'data': {
                    'orderId': f'EPR-{int(time.time())}',
                    'status': 'pending',
                    'totalAmount': 299.97,
                    'currency': 'USD',
                    'createdAt': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        
        # Order status - api/v1/order/123
        elif 'order' in endpoint and method == 'GET':
            order_id = endpoint.split('/')[-1]
            return {
                'success': True,
                'code': 0,
                'data': {
                    'orderId': order_id,
                    'status': 'processing',
                    'trackingNumber': f'TRK-{order_id}',
                    'estimatedDelivery': '3-5 days'
                }
            }
        
        # Shipping methods
        elif 'shipping' in endpoint and 'methods' in endpoint:
            return {
                'success': True,
                'code': 0,
                'data': [
                    {'id': 1, 'name': 'Standard Shipping', 'cost': 5.99, 'days': '7-15'},
                    {'id': 2, 'name': 'Express Shipping', 'cost': 19.99, 'days': '3-5'},
                    {'id': 3, 'name': 'Economy Shipping', 'cost': 2.99, 'days': '15-30'}
                ]
            }
        
        # Shipping calculation
        elif 'shipping' in endpoint and 'calculate' in endpoint:
            return {
                'success': True,
                'code': 0,
                'data': {
                    'shippingCost': 8.99,
                    'currency': 'USD',
                    'estimatedDays': 10
                }
            }
        
        # Unknown endpoint
        return {
            'success': False,
            'code': 404,
            'message': 'Unknown endpoint',
            'endpoint': endpoint
        }
    
    def test_connection(self):
        """Test API connection"""
        return self._make_request('api/v1/products', method='GET', data={'page': 1, 'pageSize': 1})
    
    def get_products(self, category=None, page=1, pageSize=20):
        """Get product list"""
        data = {
            'page': page,
            'pageSize': pageSize
        }
        if category:
            data['category'] = category
        
        return self._make_request('api/v1/products', method='GET', data=data)
    
    def get_product_detail(self, product_id):
        """Get product details"""
        return self._make_request(f'api/v1/product/{product_id}', method='GET')
    
    def create_order(self, order_data):
        """Create order
        
        Args:
            order_data (dict): Order information
                - customer_name: Customer name
                - customer_email: Email
                - customer_phone: Phone
                - items: List of items [{'product_id': 123, 'quantity': 1}]
                - shipping_address: Delivery address
                - payment_method: Payment method
        """
        return self._make_request('api/v1/order', method='POST', data=order_data)
    
    def get_order_status(self, order_id):
        """Check order status"""
        return self._make_request(f'api/v1/order/{order_id}', method='GET')
    
    def get_shipping_methods(self):
        """Get available shipping methods"""
        return self._make_request('api/v1/shipping/methods', method='GET')
    
    def calculate_shipping(self, postal_code, weight):
        """Calculate shipping cost"""
        data = {
            'postal_code': postal_code,
            'weight': weight
        }
        return self._make_request('api/v1/shipping/calculate', method='POST', data=data)


# Test function
def test_eprollo_api():
    """Test Eprollo API with test credentials"""
    service = EprolloAPIService()
    
    print("="*60)
    print("🧪 EPROLLO API TEST")
    print("="*60)
    
    # Test 1: Connection
    print("\n1️⃣ Testing Connection...")
    result = service.test_connection()
    print(f"✅ Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # Test 2: Get Products
    print("\n2️⃣ Testing Get Products...")
    result = service.get_products(page=1, pageSize=5)
    print(f"✅ Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # Test 3: Get Product Detail
    print("\n3️⃣ Testing Get Product Detail...")
    result = service.get_product_detail(product_id=1)
    print(f"✅ Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # Test 4: Get Shipping Methods
    print("\n4️⃣ Testing Shipping Methods...")
    result = service.get_shipping_methods()
    print(f"✅ Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # Test 5: Create Test Order
    print("\n5️⃣ Testing Create Order...")
    order_data = {
        'customer_name': 'Test Kullanıcı',
        'customer_email': 'test@example.com',
        'customer_phone': '+90 555 123 4567',
        'items': [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ],
        'shipping_address': {
            'street': 'Test Sokak No:1',
            'city': 'İstanbul',
            'postal_code': '34000',
            'country': 'TR'
        },
        'payment_method': 'credit_card'
    }
    result = service.create_order(order_data)
    print(f"✅ Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    print("\n" + "="*60)
    print("✅ Test Completed!")
    print("="*60)


if __name__ == '__main__':
    test_eprollo_api()
