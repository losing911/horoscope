"""
Gerçek astronomik hesaplamalar için Swiss Ephemeris servisi
"""
from datetime import datetime
from typing import Optional, Tuple, Dict
import logging

try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except ImportError:
    SWISSEPH_AVAILABLE = False
    logging.warning("pyswisseph kütüphanesi yüklü değil. Basit algoritmalar kullanılacak.")

try:
    from geopy.geocoders import Nominatim
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    logging.warning("geopy kütüphanesi yüklü değil. Varsayılan koordinatlar kullanılacak.")

from .models import ZodiacSign

logger = logging.getLogger(__name__)


class AstronomyService:
    """Swiss Ephemeris ile gerçek astronomik hesaplamalar"""
    
    # Varsayılan koordinatlar (İstanbul)
    DEFAULT_LAT = 41.0082
    DEFAULT_LON = 28.9784
    
    # Burç limitleri (Tropical Zodiac)
    ZODIAC_LIMITS = [
        (0, 30),      # Koç
        (30, 60),     # Boğa
        (60, 90),     # İkizler
        (90, 120),    # Yengeç
        (120, 150),   # Aslan
        (150, 180),   # Başak
        (180, 210),   # Terazi
        (210, 240),   # Akrep
        (240, 270),   # Yay
        (270, 300),   # Oğlak
        (300, 330),   # Kova
        (330, 360),   # Balık
    ]
    
    def __init__(self):
        """Swiss Ephemeris'i başlat"""
        if SWISSEPH_AVAILABLE:
            # Swiss Ephemeris veri yolunu ayarla (opsiyonel)
            # swe.set_ephe_path('/path/to/ephemeris/files')
            pass
    
    def get_coordinates(self, place_name: str) -> Tuple[float, float]:
        """
        Şehir adından koordinat al
        
        Args:
            place_name: Şehir adı (örn: "Ankara, Türkiye")
            
        Returns:
            (latitude, longitude) tuple
        """
        if not GEOPY_AVAILABLE or not place_name:
            logger.info(f"Varsayılan koordinatlar kullanılıyor: İstanbul ({self.DEFAULT_LAT}, {self.DEFAULT_LON})")
            return self.DEFAULT_LAT, self.DEFAULT_LON
        
        try:
            geolocator = Nominatim(user_agent="tarot-yorum-app")
            location = geolocator.geocode(place_name, timeout=10)
            
            if location:
                logger.info(f"{place_name} için koordinatlar bulundu: ({location.latitude}, {location.longitude})")
                return location.latitude, location.longitude
            else:
                logger.warning(f"{place_name} için koordinat bulunamadı, varsayılan kullanılıyor")
                return self.DEFAULT_LAT, self.DEFAULT_LON
                
        except Exception as e:
            logger.error(f"Geocoding hatası: {e}")
            return self.DEFAULT_LAT, self.DEFAULT_LON
    
    def datetime_to_julian(self, dt: datetime) -> float:
        """
        Datetime'ı Julian Day'e çevir
        
        Args:
            dt: Python datetime objesi
            
        Returns:
            Julian Day Number (float)
        """
        if SWISSEPH_AVAILABLE:
            jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
            return jd
        else:
            # Basit yaklaşım (hassas değil)
            a = (14 - dt.month) // 12
            y = dt.year + 4800 - a
            m = dt.month + 12 * a - 3
            jd = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
            jd += (dt.hour - 12) / 24.0 + dt.minute / 1440.0
            return jd
    
    def get_planet_position(self, jd: float, planet: int) -> Tuple[float, float]:
        """
        Bir gezegenin pozisyonunu hesapla
        
        Args:
            jd: Julian Day
            planet: Gezegen ID (swe.SUN, swe.MOON, vb.)
            
        Returns:
            (longitude, latitude) tuple (derece)
        """
        if not SWISSEPH_AVAILABLE:
            logger.warning("Swiss Ephemeris yok, basit hesaplama kullanılıyor")
            return 0.0, 0.0
        
        try:
            # Pozisyonu hesapla (SEFLG_SWIEPH = Swiss Ephemeris kullan)
            result = swe.calc_ut(jd, planet, swe.FLG_SWIEPH)
            longitude = result[0][0]  # Ekliptik boylam
            latitude = result[0][1]   # Ekliptik enlem
            return longitude, latitude
        except Exception as e:
            logger.error(f"Gezegen pozisyon hesaplama hatası: {e}")
            return 0.0, 0.0
    
    def longitude_to_zodiac(self, longitude: float) -> int:
        """
        Ekliptik boylamı burç sırasına çevir
        
        Args:
            longitude: Ekliptik boylam (0-360 derece)
            
        Returns:
            Burç order (1-12)
        """
        # Boylamı 0-360 aralığına normalize et
        longitude = longitude % 360
        
        # Hangi burç aralığında olduğunu bul
        for i, (start, end) in enumerate(self.ZODIAC_LIMITS):
            if start <= longitude < end:
                return i + 1  # Order 1'den başlıyor
        
        # Balık burcu son (330-360)
        return 12
    
    def calculate_moon_sign(
        self, 
        birth_date: datetime, 
        birth_place: Optional[str] = None
    ) -> Optional[ZodiacSign]:
        """
        Gerçek Ay burcunu hesapla
        
        Args:
            birth_date: Doğum tarihi ve saati
            birth_place: Doğum yeri (şehir adı)
            
        Returns:
            ZodiacSign objesi veya None
        """
        if not SWISSEPH_AVAILABLE:
            logger.warning("Swiss Ephemeris yok, basit ay burcu hesaplanıyor")
            # Fallback: ay bazlı basit hesaplama
            month = birth_date.month
            try:
                return ZodiacSign.objects.get(order=month)
            except ZodiacSign.DoesNotExist:
                return None
        
        try:
            # Julian Day'e çevir
            jd = self.datetime_to_julian(birth_date)
            
            # Ay'ın pozisyonunu hesapla
            moon_longitude, _ = self.get_planet_position(jd, swe.MOON)
            
            # Burca çevir
            zodiac_order = self.longitude_to_zodiac(moon_longitude)
            
            logger.info(f"Ay pozisyonu: {moon_longitude:.2f}° -> Burç order: {zodiac_order}")
            
            return ZodiacSign.objects.get(order=zodiac_order)
            
        except Exception as e:
            logger.error(f"Ay burcu hesaplama hatası: {e}")
            return None
    
    def calculate_ascendant(
        self,
        birth_date: datetime,
        latitude: float,
        longitude: float
    ) -> Optional[ZodiacSign]:
        """
        Gerçek Yükselen burcunu hesapla
        
        Args:
            birth_date: Doğum tarihi ve saati
            latitude: Enlem
            longitude: Boylam
            
        Returns:
            ZodiacSign objesi veya None
        """
        if not SWISSEPH_AVAILABLE:
            logger.warning("Swiss Ephemeris yok, basit yükselen hesaplanıyor")
            # Fallback: saat bazlı basit hesaplama
            hour = birth_date.hour
            ascendant_order = (hour // 2) + 1
            if ascendant_order > 12:
                ascendant_order = ascendant_order % 12
            try:
                return ZodiacSign.objects.get(order=ascendant_order)
            except ZodiacSign.DoesNotExist:
                return None
        
        try:
            # Julian Day'e çevir
            jd = self.datetime_to_julian(birth_date)
            
            # Ev sistemini hesapla (Placidus - en yaygın)
            # swe.houses(jd, lat, lon, b'P') -> (cusps, ascmc)
            houses = swe.houses(jd, latitude, longitude, b'P')
            ascendant_longitude = houses[1][0]  # ascmc[0] = Ascendant
            
            # Burca çevir
            zodiac_order = self.longitude_to_zodiac(ascendant_longitude)
            
            logger.info(f"Yükselen pozisyonu: {ascendant_longitude:.2f}° -> Burç order: {zodiac_order}")
            
            return ZodiacSign.objects.get(order=zodiac_order)
            
        except Exception as e:
            logger.error(f"Yükselen burç hesaplama hatası: {e}")
            return None
    
    def calculate_all_planets(
        self,
        birth_date: datetime,
        latitude: float,
        longitude: float
    ) -> Dict[str, Dict]:
        """
        Tüm gezegenlerin pozisyonlarını hesapla
        
        Args:
            birth_date: Doğum tarihi ve saati
            latitude: Enlem
            longitude: Boylam
            
        Returns:
            Gezegen bilgileri dictionary
        """
        if not SWISSEPH_AVAILABLE:
            logger.warning("Swiss Ephemeris yok, gezegen hesaplamaları yapılamıyor")
            return {}
        
        planets = {
            'sun': swe.SUN,
            'moon': swe.MOON,
            'mercury': swe.MERCURY,
            'venus': swe.VENUS,
            'mars': swe.MARS,
            'jupiter': swe.JUPITER,
            'saturn': swe.SATURN,
            'uranus': swe.URANUS,
            'neptune': swe.NEPTUNE,
            'pluto': swe.PLUTO,
        }
        
        results = {}
        jd = self.datetime_to_julian(birth_date)
        
        for name, planet_id in planets.items():
            try:
                planet_longitude, _ = self.get_planet_position(jd, planet_id)
                zodiac_order = self.longitude_to_zodiac(planet_longitude)
                
                zodiac_sign = ZodiacSign.objects.get(order=zodiac_order)
                
                results[name] = {
                    'longitude': planet_longitude,
                    'zodiac_order': zodiac_order,
                    'zodiac_name': zodiac_sign.name,
                    'zodiac_slug': zodiac_sign.slug,
                }
                
            except Exception as e:
                logger.error(f"{name} gezegeni hesaplama hatası: {e}")
                results[name] = None
        
        # Yükselen burcu da ekle
        try:
            houses = swe.houses(jd, latitude, longitude, b'P')
            ascendant_longitude = houses[1][0]
            zodiac_order = self.longitude_to_zodiac(ascendant_longitude)
            zodiac_sign = ZodiacSign.objects.get(order=zodiac_order)
            
            results['ascendant'] = {
                'longitude': ascendant_longitude,
                'zodiac_order': zodiac_order,
                'zodiac_name': zodiac_sign.name,
                'zodiac_slug': zodiac_sign.slug,
            }
        except Exception as e:
            logger.error(f"Yükselen hesaplama hatası: {e}")
            results['ascendant'] = None
        
        return results
    
    def get_planet_info_for_ai(self, planets: Dict[str, Dict]) -> str:
        """
        Gezegen bilgilerini AI için formatlı string'e çevir
        
        Args:
            planets: calculate_all_planets() sonucu
            
        Returns:
            Formatlı string
        """
        if not planets:
            return "Gezegen bilgileri mevcut değil."
        
        lines = ["GEZEGENLERİN KONUMLARI:"]
        
        planet_names = {
            'sun': '☀️ Güneş',
            'moon': '🌙 Ay',
            'mercury': '☿️ Merkür',
            'venus': '♀️ Venüs',
            'mars': '♂️ Mars',
            'jupiter': '♃ Jüpiter',
            'saturn': '♄ Satürn',
            'uranus': '♅ Uranüs',
            'neptune': '♆ Neptün',
            'pluto': '♇ Plüton',
            'ascendant': '⬆️ Yükselen',
        }
        
        for key, info in planets.items():
            if info:
                name = planet_names.get(key, key)
                lines.append(f"{name}: {info['zodiac_name']} ({info['longitude']:.2f}°)")
        
        return "\n".join(lines)
