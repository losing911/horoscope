# 🌍 Django Çoklu Dil Desteği Rehberi

## Kurulum Tamamlandı! ✅

Django projesi artık 4 dili destekliyor:
- 🇹🇷 Türkçe (varsayılan)
- 🇬🇧 İngilizce
- 🇩🇪 Almanca
- 🇫🇷 Fransızça

---

## 1️⃣ Template'lerde Çeviri Kullanımı

### Basit Metin Çevirisi
```django
{% load i18n %}

<h1>{% trans "Hoş Geldiniz" %}</h1>
<p>{% trans "AI destekli tarot falı" %}</p>
```

### Değişkenli Çeviri
```django
{% load i18n %}

{% blocktrans with name=user.username %}
Merhaba {{ name }}, nasılsın?
{% endblocktrans %}
```

### Çoğul Çeviri
```django
{% load i18n %}

{% blocktrans count counter=product_count %}
{{ counter }} ürün bulundu
{% plural %}
{{ counter }} ürün bulundu
{% endblocktrans %}
```

---

## 2️⃣ Python Kodunda Çeviri

### Views.py'de Çeviri
```python
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

# View içinde
def my_view(request):
    message = _("Sepete eklendi")
    messages.success(request, message)
    
# Model field'larda (lazy kullan)
class Product(models.Model):
    name = models.CharField(
        _lazy("Ürün Adı"), 
        max_length=200
    )
```

### Forms.py'de Çeviri
```python
from django.utils.translation import gettext_lazy as _

class ContactForm(forms.Form):
    name = forms.CharField(
        label=_("İsim"),
        widget=forms.TextInput(attrs={
            'placeholder': _("Adınızı girin")
        })
    )
```

---

## 3️⃣ Çeviri Dosyalarını Oluşturma

### Adım 1: Çeviri İşaretleri Ekle
Template'lerinizi ve Python kodlarınızı `{% trans %}` ve `_()` ile işaretleyin.

### Adım 2: Çeviri Dosyalarını Oluştur
```powershell
# Windows PowerShell
.\make_translations.ps1

# Veya manuel:
.venv\Scripts\python.exe manage.py makemessages -l en --ignore=.venv
.venv\Scripts\python.exe manage.py makemessages -l de --ignore=.venv
.venv\Scripts\python.exe manage.py makemessages -l fr --ignore=.venv
```

### Adım 3: Çevirileri Düzenle
`locale/en/LC_MESSAGES/django.po` dosyasını aç:

```po
msgid "Hoş Geldiniz"
msgstr "Welcome"

msgid "Sepete Ekle"
msgstr "Add to Cart"

msgid "Sepetim"
msgstr "My Cart"
```

### Adım 4: Çevirileri Derle
```powershell
.venv\Scripts\python.exe manage.py compilemessages
```

### Adım 5: Server'ı Yeniden Başlat
```powershell
.venv\Scripts\python.exe manage.py runserver 8080
```

---

## 4️⃣ Örnek Çeviriler

### Shop Modülü için Hazır Çeviriler

#### Türkçe → İngilizce
```
Mağaza → Shop
Ürünler → Products
Sepetim → My Cart
Sepete Ekle → Add to Cart
Satın Al → Buy Now
Sipariş Ver → Place Order
Siparişlerim → My Orders
Kategori → Category
Fiyat → Price
Stok → Stock
Ödeme → Payment
Teslimat → Delivery
```

#### Türkçe → Almanca
```
Mağaza → Geschäft
Ürünler → Produkte
Sepetim → Mein Warenkorb
Sepete Ekle → In den Warenkorb
Satın Al → Jetzt kaufen
Sipariş Ver → Bestellung aufgeben
Siparişlerim → Meine Bestellungen
Kategori → Kategorie
Fiyat → Preis
Stok → Lager
Ödeme → Zahlung
Teslimat → Lieferung
```

#### Türkçe → Fransızca
```
Mağaza → Boutique
Ürünler → Produits
Sepetim → Mon Panier
Sepete Ekle → Ajouter au panier
Satın Al → Acheter maintenant
Sipariş Ver → Passer commande
Siparişlerim → Mes Commandes
Kategori → Catégorie
Fiyat → Prix
Stok → Stock
Ödeme → Paiement
Teslimat → Livraison
```

---

## 5️⃣ URL'lerde Dil Desteği

### Dil Prefix'li URL'ler
- Türkçe: `https://tarot-yorum.fun/shop/`
- İngilizce: `https://tarot-yorum.fun/en/shop/`
- Almanca: `https://tarot-yorum.fun/de/shop/`
- Fransızça: `https://tarot-yorum.fun/fr/shop/`

### Dil Değiştirme
Navbar'daki dil seçici ile otomatik değişir ve cookie'de saklanır.

---

## 6️⃣ Hızlı Başlangıç Template Örnekleri

### base.html'e Eklenecek Çeviriler
```django
{% load i18n %}

<!-- Navbar -->
<li><a href="{% url 'shop:product_list' %}">{% trans "Mağaza" %}</a></li>
<li><a href="{% url 'shop:cart' %}">{% trans "Sepetim" %}</a></li>
<li><a href="{% url 'shop:order_list' %}">{% trans "Siparişlerim" %}</a></li>

<!-- Footer -->
<h5>{% trans "Hakkımızda" %}</h5>
<p>{% trans "AI destekli tarot falı ve astroloji platformu" %}</p>
```

### product_list.html
```django
{% load i18n %}

<h1>{% trans "Ürünler" %}</h1>
<button>{% trans "Sepete Ekle" %}</button>
<span>{% trans "Stokta" %}</span>
<span>{% trans "Tükendi" %}</span>
```

### cart.html
```django
{% load i18n %}

<h1>{% trans "Alışveriş Sepetim" %}</h1>
<button>{% trans "Siparişi Tamamla" %}</button>
<span>{% trans "Ara Toplam" %}: {{ cart.subtotal }} ₺</span>
<span>{% trans "Kargo" %}: {{ cart.shipping_cost }} ₺</span>
```

---

## 7️⃣ JavaScript'te Çeviri

Django çevirilerini JavaScript'e aktarmak için:

```django
<script>
    const translations = {
        'added_to_cart': "{% trans 'Ürün sepete eklendi' %}",
        'error': "{% trans 'Bir hata oluştu' %}",
        'success': "{% trans 'İşlem başarılı' %}"
    };
    
    console.log(translations.added_to_cart);
</script>
```

---

## 8️⃣ Test Etme

### Browser'da Test
1. Server'ı başlat: `python manage.py runserver 8080`
2. Siteye gir: `http://localhost:8080/`
3. Navbar'dan dil seç (🇹🇷 🇬🇧 🇩🇪 🇫🇷)
4. Sayfalar arasında gezin

### URL'den Test
- `http://localhost:8080/` (Türkçe)
- `http://localhost:8080/en/` (İngilizce)
- `http://localhost:8080/de/` (Almanca)
- `http://localhost:8080/fr/` (Fransızca)

---

## 9️⃣ Production'a Deploy

### 1. Çeviri Dosyalarını Derle
```bash
python manage.py compilemessages
```

### 2. Dosyaları Yükle
```bash
# locale/ klasörünü sunucuya yükle
scp -r locale/ django@159.89.108.100:/home/django/projects/horoscope/

# Güncellenmiş settings.py ve urls.py
scp tarot_project/settings.py django@159.89.108.100:/home/django/projects/horoscope/tarot_project/
scp tarot_project/urls.py django@159.89.108.100:/home/django/projects/horoscope/tarot_project/
```

### 3. Server'da Compile
```bash
ssh django@159.89.108.100
cd /home/django/projects/horoscope
source venv/bin/activate
python manage.py compilemessages
sudo systemctl restart gunicorn
```

---

## 🎯 Önemli Notlar

1. **Performans**: Çeviri dosyaları cache'lenir, değişiklik sonrası server restart gerekir.

2. **SEO**: Her dil için ayrı URL'ler SEO dostu.

3. **Cookie**: Dil tercihi `django_language` cookie'sinde saklanır.

4. **Varsayılan Dil**: Türkçe varsayılan, prefix yok (`/` yerine `/en/`, `/de/`, `/fr/`)

5. **Admin Panel**: Django admin otomatik çevrilir, ek işlem gerekmez.

---

## 📚 Kaynaklar

- Django i18n Docs: https://docs.djangoproject.com/en/5.0/topics/i18n/
- Rosetta (Web-based translation): `pip install django-rosetta`
- Gettext Manual: https://www.gnu.org/software/gettext/manual/

---

**Hazırlayan:** GitHub Copilot  
**Tarih:** 15 Ekim 2025
