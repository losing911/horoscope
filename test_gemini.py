#!/usr/bin/env python
"""
Gemini API Test Script
Bu script Gemini API'nin çalışıp çalışmadığını test eder
"""
import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tarot_project.settings')
django.setup()

from tarot.models import SiteSettings, TarotCard
from tarot.services import AIService
import logging

# Logging yapılandır
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s %(asctime)s %(message)s'
)
logger = logging.getLogger(__name__)

def test_gemini_connection():
    """Gemini bağlantısını test et"""
    print("\n" + "="*80)
    print("🧪 GEMINI API TEST BAŞLATIYOR")
    print("="*80 + "\n")
    
    # 1. Site ayarlarını kontrol et
    print("1️⃣ Site Ayarları Kontrol Ediliyor...")
    settings = SiteSettings.load()
    
    print(f"   📝 Varsayılan Provider: {settings.default_ai_provider}")
    print(f"   📝 Gemini Model: {settings.gemini_model}")
    print(f"   🔑 Gemini API Key: {'✅ Mevcut' if settings.gemini_api_key else '❌ YOK!'}")
    
    if settings.gemini_api_key:
        print(f"   🔑 API Key uzunluğu: {len(settings.gemini_api_key)} karakter")
        print(f"   🔑 API Key başlangıcı: {settings.gemini_api_key[:15]}...")
    else:
        print("   ❌ HATA: Gemini API Key bulunamadı!")
        print("   💡 Çözüm: http://127.0.0.1:8000/admin/settings/ adresinden API key ekleyin")
        return False
    
    print("\n2️⃣ Gemini API Bağlantısı Test Ediliyor...")
    
    try:
        # AI Service oluştur
        print("   🤖 AIService başlatılıyor...")
        ai_service = AIService(provider_name='gemini')
        print("   ✅ AIService başlatıldı")
        
        # Test kartı hazırla
        print("\n3️⃣ Test Verisi Hazırlanıyor...")
        test_card = TarotCard.objects.first()
        
        if not test_card:
            print("   ❌ Veritabanında kart bulunamadı!")
            return False
        
        print(f"   🎴 Test kartı: {test_card.name}")
        
        test_cards = [{
            'position': 1,
            'card': test_card,
            'is_reversed': False
        }]
        
        # Test sorusu
        test_question = "Bu bir test sorusudur. Lütfen kısa bir yanıt ver."
        test_spread = "Test Yayılımı"
        
        print("\n4️⃣ Gemini'ye İstek Gönderiliyor...")
        print(f"   ❓ Soru: {test_question}")
        print(f"   🎴 Kart: {test_card.name}")
        
        # Yorum oluştur
        interpretation = ai_service.generate_interpretation(
            question=test_question,
            cards=test_cards,
            spread_name=test_spread
        )
        
        print("\n5️⃣ Yanıt Alındı!")
        print("   " + "="*76)
        print(f"   📄 Yorum uzunluğu: {len(interpretation)} karakter")
        print("   " + "="*76)
        print(f"\n{interpretation}\n")
        print("   " + "="*76)
        
        print("\n✅ TEST BAŞARILI! Gemini API çalışıyor! 🎉\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST BAŞARISIZ!")
        print(f"   Hata: {str(e)}")
        print(f"   Hata Tipi: {type(e).__name__}")
        
        import traceback
        print("\n📋 Detaylı Hata:")
        print(traceback.format_exc())
        
        print("\n💡 Olası Çözümler:")
        print("   1. API Key'in doğru olduğundan emin olun")
        print("   2. https://makersuite.google.com/app/apikey adresinden key'i kontrol edin")
        print("   3. Model adının doğru olduğundan emin olun")
        print("   4. İnternet bağlantınızı kontrol edin")
        
        return False

def check_api_key():
    """API Key formatını kontrol et"""
    print("\n" + "="*80)
    print("🔍 API KEY DETAYLI KONTROL")
    print("="*80 + "\n")
    
    settings = SiteSettings.load()
    api_key = settings.gemini_api_key
    
    if not api_key:
        print("❌ API Key bulunamadı!\n")
        return False
    
    print(f"✅ API Key bulundu!")
    print(f"   Uzunluk: {len(api_key)} karakter")
    print(f"   İlk 10 karakter: {api_key[:10]}...")
    print(f"   Son 10 karakter: ...{api_key[-10:]}")
    
    # Format kontrolü
    if api_key.startswith('AI'):
        print("   ✅ Format doğru görünüyor (AIza... ile başlıyor)")
    else:
        print("   ⚠️ Uyarı: Gemini API key'leri genellikle 'AIza' ile başlar")
    
    # Boşluk kontrolü
    if ' ' in api_key:
        print("   ⚠️ Uyarı: API Key'de boşluk var! Bu hatalara neden olabilir.")
    
    # Satır sonu kontrolü
    if '\n' in api_key or '\r' in api_key:
        print("   ⚠️ Uyarı: API Key'de satır sonu karakteri var!")
    
    print()
    return True

if __name__ == '__main__':
    print("\n🎯 DJTarot - Gemini API Test Aracı\n")
    
    # 1. API Key kontrolü
    check_api_key()
    
    # 2. Bağlantı testi
    test_gemini_connection()
    
    print("="*80)
    print("TEST TAMAMLANDI")
    print("="*80 + "\n")
    
    print("💡 Log dosyasını kontrol edin: logs/ai_service.log\n")
