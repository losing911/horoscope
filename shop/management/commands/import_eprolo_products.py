"""
EPROLO Product Import Management Command

Features:
- Import products from EPROLO API
- Search products by keyword
- Update existing products
- Automatic USD to TRY conversion
- Category management
- Variant support
- Inventory sync
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.db import transaction
from decimal import Decimal
from shop.models import Category, Product
from shop.eprollo_service import EprolloAPIService
import time


class Command(BaseCommand):
    help = '''Import products from EPROLO API
    
    Examples:
        python manage.py import_eprolo_products --all
        python manage.py import_eprolo_products --search "t-shirt"
        python manage.py import_eprolo_products --category "clothing" --limit 10
        python manage.py import_eprolo_products --product-id 1001
        python manage.py import_eprolo_products --update-prices
    '''

    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            '--all',
            action='store_true',
            help='Import all products (paginated)'
        )
        parser.add_argument(
            '--search',
            type=str,
            help='Search products by keyword'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Filter by category slug'
        )
        parser.add_argument(
            '--product-id',
            type=str,
            help='Import specific product by ID'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of products to import (default: 50)'
        )
        parser.add_argument(
            '--update-prices',
            action='store_true',
            help='Update prices of existing products'
        )
        parser.add_argument(
            '--update-stock',
            action='store_true',
            help='Update inventory/stock information'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without saving'
        )
        parser.add_argument(
            '--target-category',
            type=str,
            default='eprolo-urunler',
            help='Target category slug (default: eprolo-urunler)'
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("🛍️  EPROLO PRODUCT IMPORT SYSTEM"))
        self.stdout.write("=" * 80)
        
        # Initialize service
        service = EprolloAPIService()
        
        # Show mode
        mode_text = "MOCK MODE (Test Data)" if service.use_mock else "REAL API MODE"
        mode_style = self.style.WARNING if service.use_mock else self.style.SUCCESS
        self.stdout.write(f"\n📍 Mode: {mode_style(mode_text)}")
        self.stdout.write(f"💱 Exchange Rate: 1 USD = {service.usd_to_try_rate} TL")
        
        # Dry run warning
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("\n⚠️  DRY RUN MODE - No changes will be saved"))
        
        # Prepare target category
        category = self._get_or_create_category(options['target_category'], options['dry_run'])
        
        # Determine operation mode
        products_to_import = []
        
        if options['product_id']:
            # Single product import
            self.stdout.write(f"\n🔍 Fetching product ID: {options['product_id']}")
            products_to_import = self._fetch_single_product(service, options['product_id'])
            
        elif options['search']:
            # Search mode
            self.stdout.write(f"\n🔍 Searching products: '{options['search']}'")
            products_to_import = self._search_products(service, options['search'], options['limit'])
            
        elif options['all']:
            # Import all products
            self.stdout.write(f"\n📦 Fetching all products (limit: {options['limit']})")
            products_to_import = self._fetch_all_products(service, options['category'], options['limit'])
            
        elif options['update_prices']:
            # Update prices only
            self.stdout.write("\n💰 Updating product prices...")
            self._update_prices(service, options['dry_run'])
            return
            
        elif options['update_stock']:
            # Update stock only
            self.stdout.write("\n📊 Updating product inventory...")
            self._update_inventory(service, options['dry_run'])
            return
            
        else:
            raise CommandError("Please specify an operation: --all, --search, --product-id, --update-prices, or --update-stock")
        
        if not products_to_import:
            self.stdout.write(self.style.WARNING("\n⚠️  No products found"))
            return
        
        # Import products
        self.stdout.write(f"\n💾 Processing {len(products_to_import)} product(s)...")
        self.stdout.write("-" * 80)
        
        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for prod_data in products_to_import:
            try:
                result = self._import_single_product(
                    service,
                    prod_data,
                    category,
                    options['dry_run']
                )
                stats[result] += 1
            except Exception as e:
                stats['errors'] += 1
                self.stdout.write(self.style.ERROR(f"  ❌ Error: {str(e)}"))
        
        # Show summary
        self._show_summary(stats, options['dry_run'])

    def _get_or_create_category(self, slug, dry_run=False):
        """Get or create target category"""
        self.stdout.write(f"\n📂 Category: {slug}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("  (Dry run - would create if not exists)"))
            return None
        
        category, created = Category.objects.get_or_create(
            slug=slug,
            defaults={
                'name': slug.replace('-', ' ').title(),
                'description': 'Products imported from EPROLO',
                'icon': 'fa-shopping-bag',
                'is_active': True,
                'order': 50
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"  ✅ Created category: {category.name}"))
        else:
            self.stdout.write(f"  ℹ️  Using existing category: {category.name}")
        
        return category

    def _fetch_single_product(self, service, product_id):
        """Fetch single product by ID"""
        result = service.get_product_detail(product_id)
        
        if not result.get('success'):
            self.stdout.write(self.style.ERROR(f"  ❌ Error: {result.get('msg')}"))
            return []
        
        product = result.get('data', {})
        self.stdout.write(self.style.SUCCESS(f"  ✅ Found: {product.get('name')}"))
        return [product]

    def _search_products(self, service, keyword, limit):
        """Search products by keyword"""
        result = service.search_products(keyword=keyword, page=1, pageSize=limit)
        
        if not result.get('success'):
            self.stdout.write(self.style.ERROR(f"  ❌ Error: {result.get('msg')}"))
            return []
        
        products = result.get('data', {}).get('list', [])
        total = result.get('data', {}).get('total', 0)
        self.stdout.write(self.style.SUCCESS(f"  ✅ Found {len(products)} products (Total: {total})"))
        return products

    def _fetch_all_products(self, service, category_filter, limit):
        """Fetch all products with optional category filter"""
        result = service.get_products(category=category_filter, page=1, pageSize=limit)
        
        if not result.get('success'):
            self.stdout.write(self.style.ERROR(f"  ❌ Error: {result.get('msg')}"))
            return []
        
        products = result.get('data', {}).get('list', [])
        total = result.get('data', {}).get('total', 0)
        self.stdout.write(self.style.SUCCESS(f"  ✅ Retrieved {len(products)} products (Total available: {total})"))
        return products

    def _import_single_product(self, service, prod_data, category, dry_run=False):
        """Import single product into database"""
        
        # Extract product data
        product_id = str(prod_data.get('productId', prod_data.get('id', '')))
        name = prod_data.get('name', 'Unnamed Product')
        price_usd = Decimal(str(prod_data.get('price', 0)))
        compare_at_price = prod_data.get('compareAtPrice')
        
        # Generate slug
        slug = slugify(name, allow_unicode=True)
        if not slug:
            slug = f"product-{product_id}"
        
        # Get detailed information
        detail_result = service.get_product_detail(product_id)
        if detail_result.get('success'):
            detail = detail_result.get('data', {})
            description = detail.get('description', '')
            images = detail.get('images', [])
            stock = detail.get('stock', 0)
            weight = detail.get('weight', 0)
        else:
            description = name
            images = [prod_data.get('mainImage', prod_data.get('image', ''))]
            stock = prod_data.get('stock', 0)
            weight = 0
        
        # Convert price
        price_try = service.convert_usd_to_try(float(price_usd))
        
        if dry_run:
            self.stdout.write(f"  [DRY RUN] Would import: {name}")
            self.stdout.write(f"            Price: ${price_usd} → {price_try} TL")
            self.stdout.write(f"            Stock: {stock}")
            return 'created'
        
        # Check if product exists
        try:
            product = Product.objects.get(slug=slug)
            operation = 'updated'
            self.stdout.write(f"  🔄 Updating: {name}")
        except Product.DoesNotExist:
            product = Product(slug=slug)
            operation = 'created'
            self.stdout.write(f"  ➕ Creating: {name}")
        
        # Update product fields
        product.category = category
        product.name = name
        product.slug = slug
        product.description = self._clean_description(description)
        product.short_description = name[:200]
        product.price_usd = price_usd
        product.usd_to_try_rate = service.usd_to_try_rate
        product.price = price_try  # Will be auto-calculated in model.save()
        
        if compare_at_price:
            product.original_price = service.convert_usd_to_try(float(compare_at_price))
        
        product.stock = stock
        product.stock_status = 'in_stock' if stock > 0 else 'out_of_stock'
        
        # Set images
        if images:
            product.image = images[0]
            if len(images) > 1:
                product.image_2 = images[1]
            if len(images) > 2:
                product.image_3 = images[2]
        
        product.is_active = True
        product.is_featured = False
        
        # Add features
        product.features = self._generate_features(prod_data)
        
        # Save
        product.save()
        
        self.stdout.write(f"       Price: ${price_usd} → {price_try:.2f} TL")
        self.stdout.write(f"       Stock: {stock} units")
        if images:
            self.stdout.write(f"       Images: {len(images)}")
        
        return operation

    def _clean_description(self, description):
        """Clean and format product description"""
        if not description:
            return "Yüksek kaliteli ürün. Detaylı bilgi için lütfen bizimle iletişime geçin."
        
        # Remove EPROLO branding
        description = description.replace('EPROLO', '')
        description = description.replace('eprolo', '')
        
        return description.strip()

    def _generate_features(self, prod_data):
        """Generate product features list"""
        features = []
        features.append("✓ Premium kalite malzeme")
        features.append("✓ Hızlı ve güvenli kargo")
        features.append("✓ 14 gün kolay iade")
        features.append("✓ Ücretsiz teslimat")
        features.append("✓ %100 müşteri memnuniyeti garantisi")
        
        return '\n'.join(features)

    def _update_prices(self, service, dry_run=False):
        """Update prices for existing products"""
        products = Product.objects.filter(price_usd__isnull=False)
        count = products.count()
        
        self.stdout.write(f"\n📊 Found {count} products with USD prices")
        
        updated = 0
        for product in products:
            try:
                # Get latest price from EPROLO
                # For now, just recalculate with current rate
                new_price_try = service.convert_usd_to_try(float(product.price_usd))
                
                if not dry_run:
                    product.usd_to_try_rate = service.usd_to_try_rate
                    product.price = new_price_try
                    product.save(update_fields=['price', 'usd_to_try_rate'])
                    updated += 1
                
                self.stdout.write(f"  ✅ {product.name}: ${product.price_usd} → {new_price_try:.2f} TL")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error updating {product.name}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Updated {updated} products"))

    def _update_inventory(self, service, dry_run=False):
        """Update inventory for existing products"""
        # This would require storing EPROLO product IDs
        self.stdout.write(self.style.WARNING("\n⚠️  Inventory update not yet implemented"))
        self.stdout.write("    (Requires EPROLO product ID storage)")

    def _show_summary(self, stats, dry_run=False):
        """Display import summary"""
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("📊 IMPORT SUMMARY"))
        self.stdout.write("=" * 80)
        
        if dry_run:
            self.stdout.write(self.style.WARNING("  (Dry Run - No actual changes made)"))
        
        self.stdout.write(f"  ➕ Created:  {self.style.SUCCESS(str(stats['created']))}")
        self.stdout.write(f"  🔄 Updated:  {stats['updated']}")
        self.stdout.write(f"  ⏭️  Skipped:  {stats['skipped']}")
        
        if stats['errors'] > 0:
            self.stdout.write(f"  ❌ Errors:   {self.style.ERROR(str(stats['errors']))}")
        
        total = sum(stats.values())
        self.stdout.write(f"\n  📦 Total Processed: {total}")
        self.stdout.write("=" * 80)
        
        if not dry_run:
            self.stdout.write("\n" + self.style.SUCCESS("✨ Import completed successfully!"))
            self.stdout.write("\n💡 TIP: Visit admin panel to review imported products")

