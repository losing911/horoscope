"""
Custom Middleware for Tarot Project
UTF-8 Encoding Middleware
"""


class UTF8Middleware:
    """
    Middleware to force UTF-8 encoding on all HTTP responses
    Fixes Turkish character encoding issues
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Force UTF-8 encoding on all HTML responses
        if hasattr(response, 'content') and response.get('Content-Type', '').startswith('text/html'):
            if not response.get('Content-Type', '').endswith('charset=utf-8'):
                response['Content-Type'] = 'text/html; charset=utf-8'
        
        return response
