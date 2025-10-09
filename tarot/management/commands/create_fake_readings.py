from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tarot.models import TarotCard, TarotSpread, TarotReading, AIProvider
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Fake hesaplar ve örnek tarot okumaları oluşturur'

    def handle(self, *args, **kwargs):
        self.stdout.write('Fake hesaplar ve okumalar oluşturuluyor...')
        
        # Fake kullanıcı isimleri
        fake_users = [
            'zeynep_yildiz',
            'mehmet_ay',
            'ayse_guneş',
            'ali_deniz',
            'fatma_yilmaz',
            'ahmet_kara',
        ]
        
        # Fake sorular
        fake_questions = [
            'İş hayatımda yeni bir fırsat mı beni bekliyor?',
            'Aşk hayatımda ne gibi değişiklikler olacak?',
            'Yakın zamanda mali açıdan nasıl bir dönem geçireceğim?',
            'Aile ilişkilerimde dikkat etmem gereken bir şey var mı?',
            'Kariyerimde yeni bir adım atmak için doğru zaman mı?',
            'Sevdiğim kişi ile ilişkim nasıl gelişecek?',
            'Bu yıl hangi alanlarda şanslı olacağım?',
            'Arkadaşlıklarımda dikkat etmem gereken noktalar neler?',
            'Sağlığım konusunda nelere dikkat etmeliyim?',
            'Yeni bir projeye başlamak için uygun mu?',
        ]
        
        # Fake yorumlar (şablonlar)
        interpretation_templates = [
            """## {spread_name} Yorumu

**Sorunuz:** {question}

### Kartların Mesajı

{card_meanings}

### Genel Değerlendirme

Kartlar sizin için önemli bir dönüşüm dönemini işaret ediyor. {insight1} 

{insight2}

### Tavsiyeler

- İç sesinizi dinleyin ve sezgilerinize güvenin
- Sabırlı olun, her şeyin zamanı var
- Yeni fırsatlara açık olun
- Geçmişi geride bırakıp geleceğe odaklanın

**Unutmayın:** Kartlar sadece olası yolları gösterir, kararlar hep sizin elinizde!
""",
            """## {spread_name} ile Geleceğinize Bakış

**Soru:** {question}

### Pozisyonlar

{card_meanings}

### Analiz

{insight1} Kartlar, {insight2}

### Sonuç

Bu okuma, hayatınızda önemli değişimlerin kapıda olduğunu gösteriyor. Güçlü kalın ve kendinize güvenin.

**Not:** Tarot, rehberlik eder ama kararlar size aittir!
"""
        ]
        
        insights = [
            "şu an için sabırlı olmanız gerektiğini gösteriyor",
            "yeni bir başlangıç için hazır olduğunuzu işaret ediyor",
            "geçmişteki deneyimlerinizden ders çıkarmanız gerektiğini söylüyor",
            "içsel gücünüzü keşfetmeniz için size fırsat sunuyor",
            "yakın zamanda önemli bir karar vermeniz gerekebileceğini gösteriyor",
            "etrafınızdaki insanlarla daha fazla iletişim kurmanız gerektiğini işaret ediyor",
            "duygularınıza kulak vermeniz gerektiğini söylüyor",
            "maddi konularda dikkatli olmanız gerektiğini gösteriyor",
        ]
        
        # AI Provider al
        try:
            ai_provider = AIProvider.objects.first()
            if not ai_provider:
                self.stdout.write(self.style.ERROR('AI Provider bulunamadı!'))
                return
        except:
            self.stdout.write(self.style.ERROR('AI Provider bulunamadı!'))
            return
        
        # Fake kullanıcıları oluştur veya al
        users = []
        for username in fake_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': username.split('_')[0].capitalize(),
                    'last_name': username.split('_')[1].capitalize(),
                }
            )
            if created:
                user.set_password('demo1234')
                user.save()
                self.stdout.write(f'✓ Kullanıcı oluşturuldu: {username}')
            users.append(user)
        
        # Tüm kartları ve yayılımları al
        all_cards = list(TarotCard.objects.all())
        spreads = list(TarotSpread.objects.filter(is_active=True))
        
        if not all_cards:
            self.stdout.write(self.style.ERROR('Hiç tarot kartı yok!'))
            return
        
        if not spreads:
            self.stdout.write(self.style.ERROR('Hiç yayılım yok!'))
            return
        
        # Her kullanıcı için 2-3 okuma oluştur
        total_readings = 0
        for user in users:
            num_readings = random.randint(2, 3)
            
            for _ in range(num_readings):
                spread = random.choice(spreads)
                question = random.choice(fake_questions)
                
                # Kartları seç
                selected_cards = random.sample(all_cards, spread.card_count)
                
                # Kart verilerini hazırla
                cards_data = []
                card_meanings_text = ""
                
                for i, card in enumerate(selected_cards, 1):
                    is_reversed = random.choice([True, False])
                    position_meaning = spread.positions.get(str(i), f'Pozisyon {i}')
                    meaning = card.reversed_meaning if is_reversed else card.upright_meaning
                    
                    cards_data.append({
                        'id': card.id,
                        'name': card.name,
                        'position': i,
                        'position_meaning': position_meaning,
                        'is_reversed': is_reversed,
                        'meaning': meaning,
                        'image_url': card.image_url if card.image_url else None
                    })
                    
                    direction = "(Ters)" if is_reversed else "(Düz)"
                    card_meanings_text += f"**{i}. {position_meaning} - {card.name} {direction}:**\n{meaning}\n\n"
                
                # Yorum oluştur
                template = random.choice(interpretation_templates)
                interpretation = template.format(
                    spread_name=spread.name,
                    question=question,
                    card_meanings=card_meanings_text,
                    insight1=random.choice(insights),
                    insight2=random.choice(insights)
                )
                
                # Okumayı oluştur
                reading = TarotReading.objects.create(
                    user=user,
                    spread=spread,
                    question=question,
                    cards=cards_data,
                    interpretation=interpretation,
                    ai_provider=ai_provider,
                    is_public=True  # Herkese açık yap
                )
                
                total_readings += 1
                self.stdout.write(f'  ✓ {user.username} için okuma oluşturuldu: {spread.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Toplam {len(users)} fake kullanıcı ve {total_readings} okuma oluşturuldu!'))
