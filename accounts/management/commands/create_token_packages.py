from django.core.management.base import BaseCommand
from accounts.models import TokenPackage
from decimal import Decimal


class Command(BaseCommand):
    help = 'Örnek jeton paketlerini oluşturur'

    def handle(self, *args, **options):
        packages = [
            {
                'name': 'Mini Paket',
                'token_amount': 10,
                'price': Decimal('49.99'),
                'price_usd': Decimal('1.99'),
                'bonus_tokens': 0,
                'display_order': 1
            },
            {
                'name': 'Standart Paket',
                'token_amount': 25,
                'price': Decimal('99.99'),
                'price_usd': Decimal('3.99'),
                'bonus_tokens': 5,
                'display_order': 2
            },
            {
                'name': 'Popüler Paket',
                'token_amount': 50,
                'price': Decimal('179.99'),
                'price_usd': Decimal('6.99'),
                'bonus_tokens': 15,
                'display_order': 3
            },
            {
                'name': 'Premium Paket',
                'token_amount': 100,
                'price': Decimal('299.99'),
                'price_usd': Decimal('11.99'),
                'bonus_tokens': 35,
                'display_order': 4
            },
            {
                'name': 'VIP Paket',
                'token_amount': 250,
                'price': Decimal('649.99'),
                'price_usd': Decimal('24.99'),
                'bonus_tokens': 100,
                'display_order': 5
            }
        ]

        created_count = 0
        for package_data in packages:
            package, created = TokenPackage.objects.get_or_create(
                name=package_data['name'],
                defaults=package_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {package.name} oluşturuldu ({package.total_tokens} jeton - {package.price} TL)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'• {package.name} zaten mevcut')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Toplam {created_count} yeni paket oluşturuldu')
        )
