"""
Management command to share daily horoscopes on Instagram
"""
import os
import requests
from datetime import date
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.management.base import BaseCommand
from django.conf import settings
from zodiac.models import ZodiacSign, DailyHoroscope


class Command(BaseCommand):
    help = 'Günlük burç yorumlarını Instagram\'a paylaş'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--zodiac-sign',
            type=str,
            help='Belirli bir burç için paylaş (örn: koc, boga)'
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Tarih (YYYY-MM-DD formatında, varsayılan: bugün)'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test modu (görseli kaydet ama Instagram\'a gönderme)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("📱 INSTAGRAM'A GÜNLÜK BURÇ PAYLAŞIMI"))
        self.stdout.write("="*70 + "\n")
        
        # Instagram credentials kontrolü
        from django.conf import settings
        access_token = settings.INSTAGRAM_ACCESS_TOKEN
        instagram_account_id = settings.INSTAGRAM_BUSINESS_ACCOUNT_ID
        
        if not options['test'] and (not access_token or not instagram_account_id):
            self.stdout.write(
                self.style.ERROR(
                    "❌ Instagram API bilgileri eksik!\n"
                    "   .env dosyasına ekleyin:\n"
                    "   INSTAGRAM_ACCESS_TOKEN=your-token\n"
                    "   INSTAGRAM_BUSINESS_ACCOUNT_ID=your-account-id"
                )
            )
            return
        
        # Tarih
        target_date = date.today()
        if options['date']:
            try:
                year, month, day = options['date'].split('-')
                target_date = date(int(year), int(month), int(day))
            except:
                self.stdout.write(
                    self.style.ERROR("❌ Geçersiz tarih formatı! YYYY-MM-DD kullanın")
                )
                return
        
        # Hangi burçları paylaşacağız?
        if options['zodiac_sign']:
            signs = ZodiacSign.objects.filter(slug=options['zodiac_sign'])
            if not signs.exists():
                self.stdout.write(
                    self.style.ERROR(f"❌ Burç bulunamadı: {options['zodiac_sign']}")
                )
                return
        else:
            signs = ZodiacSign.objects.all()
        
        success_count = 0
        failed_count = 0
        
        for sign in signs:
            self.stdout.write(f"\n🔄 İşleniyor: {sign.name}...")
            
            try:
                # Günlük yorumu getir
                horoscope = DailyHoroscope.objects.filter(
                    zodiac_sign=sign,
                    date=target_date
                ).first()
                
                if not horoscope:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠️  {target_date} için yorum bulunamadı")
                    )
                    failed_count += 1
                    continue
                
                # Görsel oluştur
                image_path = self._create_horoscope_image(sign, horoscope, target_date)
                self.stdout.write(f"  ✅ Görsel oluşturuldu: {image_path}")
                
                if not options['test']:
                    # Instagram'a paylaş
                    result = self._post_to_instagram(
                        image_path,
                        sign,
                        horoscope,
                        access_token,
                        instagram_account_id
                    )
                    
                    if result:
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✅ Instagram'a paylaşıldı!")
                        )
                        success_count += 1
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"  ❌ Instagram paylaşımı başarısız")
                        )
                        failed_count += 1
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✅ Test modu - görsel kaydedildi")
                    )
                    success_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Hata: {str(e)}")
                )
                failed_count += 1
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(f"📊 Başarılı: {success_count}")
        self.stdout.write(f"📊 Başarısız: {failed_count}")
        self.stdout.write("="*70 + "\n")
    
    def _create_horoscope_image(self, sign, horoscope, target_date):
        """Burç yorumu için görsel oluştur"""
        # Görsel boyutları (Instagram square post)
        width, height = 1080, 1080
        
        # Burç renklerini kullan (gradient background)
        colors = {
            'koc': ('#FF6B6B', '#FF8E53'),
            'boga': ('#4ECDC4', '#44A08D'),
            'ikizler': ('#FFE66D', '#FFAA4F'),
            'yengec': ('#95E1D3', '#6C5CE7'),
            'aslan': ('#FD79A8', '#FDCB6E'),
            'basak': ('#74B9FF', '#0984E3'),
            'terazi': ('#A29BFE', '#6C5CE7'),
            'akrep': ('#636E72', '#2D3436'),
            'yay': ('#FAB1A0', '#E17055'),
            'oglak': ('#81ECEC', '#00B894'),
            'kova': ('#DFE6E9', '#74B9FF'),
            'balik': ('#FD79A8', '#6C5CE7'),
        }
        
        color1, color2 = colors.get(sign.slug, ('#6B1B3D', '#4A0E2A'))
        
        # Hex to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        # Görsel oluştur  
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Gradient background
        for y in range(height):
            r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * y / height)
            g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * y / height)
            b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Font (varsayılan, sonra özel font eklenebilir)
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Burç adı (üstte)
        title = f"{sign.symbol} {sign.name.upper()}"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((width - title_width) / 2, 80),
            title,
            fill='white',
            font=title_font
        )
        
        # Tarih
        date_str = target_date.strftime('%d.%m.%Y')
        date_bbox = draw.textbbox((0, 0), date_str, font=subtitle_font)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(
            ((width - date_width) / 2, 180),
            date_str,
            fill='white',
            font=subtitle_font
        )
        
        # Yorum metni (ortada, çerçeve içinde)
        padding = 60
        text_y = 280
        
        # Genel yorum (kısalt)
        general_text = horoscope.general[:180] + "..." if len(horoscope.general) > 180 else horoscope.general
        
        # Metni wrap et
        lines = self._wrap_text(general_text, text_font, width - 2*padding)
        for line in lines[:6]:  # Maksimum 6 satır
            line_bbox = draw.textbbox((0, 0), line, font=text_font)
            line_width = line_bbox[2] - line_bbox[0]
            draw.text(
                ((width - line_width) / 2, text_y),
                line,
                fill='white',
                font=text_font
            )
            text_y += 50
        
        # Alt bilgi
        footer = "www.tarot-yorum.fun • AI Destekli Astroloji"
        footer_bbox = draw.textbbox((0, 0), footer, font=small_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        draw.text(
            ((width - footer_width) / 2, height - 80),
            footer,
            fill='white',
            font=small_font
        )
        
        # Kaydet
        output_dir = '/home/django/projects/horoscope/media/horoscope_images'
        os.makedirs(output_dir, exist_ok=True)
        image_path = f"{output_dir}/{sign.slug}_{target_date}.jpg"
        img.save(image_path, quality=95)
        
        return image_path
    
    def _wrap_text(self, text, font, max_width):
        """Metni satırlara böl"""
        words = text.split()
        lines = []
        current_line = []
        
        draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width > max_width:
                if len(current_line) == 1:
                    lines.append(current_line[0])
                    current_line = []
                else:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _post_to_instagram(self, image_path, sign, horoscope, access_token, account_id):
        """Instagram'a görsel paylaş"""
        try:
            # Caption oluştur
            caption = f"""🌟 {sign.name} Burcu - Günlük Yorum

{horoscope.general[:200]}...

Detaylı yorum için: www.tarot-yorum.fun

#astroloji #burç #{sign.slug} #günlükburç #fal #tarot #horoskop"""
            
            self.stdout.write(f"    Caption hazır: {len(caption)} karakter")
            
            # Görselin public URL'ini oluştur
            from django.conf import settings
            image_filename = os.path.basename(image_path)
            image_public_url = f"http://159.89.108.100/media/horoscope_images/{image_filename}"
            
            self.stdout.write(f"    📸 Görsel URL: {image_public_url}")
            
            # Instagram Graph API - Create Media Container
            base_url = "https://graph.facebook.com/v18.0"
            
            # Step 1: Create container
            container_url = f"{base_url}/{account_id}/media"
            container_params = {
                'image_url': image_public_url,
                'caption': caption,
                'access_token': access_token
            }
            
            self.stdout.write(f"    🔄 Container oluşturuluyor...")
            container_response = requests.post(container_url, params=container_params, timeout=30)
            
            if container_response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(
                        f"    ❌ Container oluşturulamadı: {container_response.text}"
                    )
                )
                return False
            
            container_data = container_response.json()
            container_id = container_data.get('id')
            
            if not container_id:
                self.stdout.write(
                    self.style.ERROR(f"    ❌ Container ID alınamadı: {container_data}")
                )
                return False
            
            self.stdout.write(f"    ✅ Container ID: {container_id}")
            
            # Step 2: Publish container
            import time
            time.sleep(2)  # Instagram'ın görseli işlemesi için bekle
            
            publish_url = f"{base_url}/{account_id}/media_publish"
            publish_params = {
                'creation_id': container_id,
                'access_token': access_token
            }
            
            self.stdout.write(f"    🔄 Post yayınlanıyor...")
            publish_response = requests.post(publish_url, params=publish_params, timeout=30)
            
            if publish_response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(
                        f"    ❌ Post yayınlanamadı: {publish_response.text}"
                    )
                )
                return False
            
            publish_data = publish_response.json()
            media_id = publish_data.get('id')
            
            if media_id:
                self.stdout.write(
                    self.style.SUCCESS(f"    ✅ Instagram Post ID: {media_id}")
                )
                return True
            else:
                self.stdout.write(
                    self.style.ERROR(f"    ❌ Media ID alınamadı: {publish_data}")
                )
                return False
            
        except requests.exceptions.Timeout:
            self.stdout.write(f"    ❌ Timeout: API yanıt vermedi")
            return False
        except Exception as e:
            self.stdout.write(f"    ❌ Instagram API hatası: {str(e)}")
            import traceback
            self.stdout.write(f"    {traceback.format_exc()}")
            return False
