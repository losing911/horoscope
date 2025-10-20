#!/usr/bin/env python
"""
Veritabanındaki mevcut sütunları kontrol eden script
Sunucuda çalıştırılmalı: python check_db_columns.py
"""
import os
import sys
import django

# Django settings'i yükle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarot_project.settings')
django.setup()

from django.db import connection

def check_columns():
    with connection.cursor() as cursor:
        # Product tablosundaki sütunları listele
        cursor.execute("PRAGMA table_info(shop_product);")
        columns = cursor.fetchall()
        
        print("\n=== shop_product tablosundaki sütunlar ===\n")
        print(f"{'ID':<5} {'Name':<30} {'Type':<20} {'NotNull':<10} {'Default':<15}")
        print("-" * 85)
        
        existing_columns = []
        for col in columns:
            col_id, name, col_type, not_null, default_val, pk = col
            existing_columns.append(name)
            print(f"{col_id:<5} {name:<30} {col_type:<20} {not_null:<10} {str(default_val):<15}")
        
        print("\n" + "=" * 85)
        print(f"\nToplam {len(columns)} sütun bulundu.\n")
        
        # Migration'da eklenecek sütunları kontrol et
        required_columns = [
            'cost_price',
            'eprolo_data',
            'eprolo_last_sync',
            'eprolo_product_id',
            'eprolo_sku',
            'eprolo_supplier',
            'eprolo_variant_id',
            'eprolo_warehouse',
            'price_usd',
            'profit_margin',
            'source',
            'usd_to_try_rate',
        ]
        
        print("=== Migration durumu ===\n")
        for col in required_columns:
            status = "✅ MEVCUT" if col in existing_columns else "❌ EKLENMELİ"
            print(f"{col:<30} {status}")
        
        print("\n" + "=" * 85)
        
        # Category tablosunu kontrol et
        cursor.execute("PRAGMA table_info(shop_category);")
        cat_columns = cursor.fetchall()
        
        print("\n=== shop_category tablosundaki EPROLO sütunları ===\n")
        eprolo_cat_columns = [
            'enable_eprolo_sync',
            'eprolo_category_id',
            'eprolo_category_name',
            'auto_activate_products',
            'custom_profit_margin'
        ]
        
        cat_column_names = [col[1] for col in cat_columns]
        for col in eprolo_cat_columns:
            status = "✅ MEVCUT" if col in cat_column_names else "❌ EKLENMELİ"
            print(f"{col:<30} {status}")

if __name__ == '__main__':
    check_columns()
