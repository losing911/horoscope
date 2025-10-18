# Tarot Yorum - AI-Powered Horoscope & Tarot Platform

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://tarot-yorum.fun)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-purple)](LICENSE)

> Modern, AI-powered astrology and tarot platform with daily horoscopes, tarot readings, and e-commerce features.

Live: [tarot-yorum.fun](https://tarot-yorum.fun)

---

## Project Overview

Tarot Yorum is an AI-powered web platform that combines traditional astrology wisdom with modern technology:

- Daily horoscopes (AI-generated for 12 zodiac signs)
- Interactive tarot readings (Celtic Cross, Three Cards, Love Reading, etc.)
- E-commerce (Zodiac rings, crystals, metaphysical products)
- Revenue tracking (Automatic USD/TRY conversion)
- User management (Django authentication)
- Admin dashboard (Order/Product/Revenue management)

---

## Key Features

### AI Integration
- **Multi-model support:** OpenAI GPT-4, Google Gemini, OpenRouter
- **Smart model selection:** Cost and performance optimization
- **Quota management:** Automatic fallback mechanism
- **Prompt engineering:** Astrology expert personality simulation

### Tarot System
- **78 tarot cards** (Major + Minor Arcana)
- **5 different spreads:** Celtic Cross, Three Cards, Love, Career, Yes/No
- **Real-time interpretation:** AI-powered
- **Visual experience:** Rider-Waite tarot images
- **Reading history:** User tarot reading logs

### E-commerce Module
- **Product management:** Categories, stock, pricing
- **USD/TRY conversion:** Automatic currency calculation
- **Order tracking:** Pending to Delivered workflow
- **Payment management:** Cash on Delivery, Credit Card, Bank Transfer
- **Revenue analytics:** Sales statistics and reporting
- **Bulk operations:** Admin panel bulk actions

### Admin Dashboard
- **Revenue indicators:** Total revenue, paid/pending orders
- **Sales analysis:** Product-based sales and revenue reports
- **Payment control:** Automatic cash on delivery processing
- **Image management:** Unsplash integration
- **Stock tracking:** Automatic stock status updates

---

## Tech Stack

### Backend
- Framework: Django 5.0 (Python 3.11)
- Database: SQLite (PostgreSQL ready for production)
- API: RESTful endpoints
- AI: OpenAI, Google Gemini, OpenRouter SDK

### Frontend
- Template Engine: Django Templates
- CSS Framework: Bootstrap 5
- Icons: Font Awesome
- Animations: Custom CSS

### DevOps
- Web Server: Nginx + Gunicorn
- SSL: Let's Encrypt
- OS: Ubuntu 22.04 LTS


### External Services
- AI Models: GPT-4o, Gemini 1.5 Pro, Claude 3.5
- Images: Unsplash API
- E-commerce: Custom integration (EPROLO ready)

---

## Project Structure

`
djtarot/
 accounts/              # User management
    models.py         # Custom user model
    views.py          # Login/Register
 blog/                  # Blog module
 shop/                  # E-commerce
    models.py         # Product, Order, Cart
    admin.py          # Revenue tracking, order management
    eprollo_service.py # Dropshipping API
    management/       # Import commands
 tarot/                 # Tarot system
    models.py         # TarotCard, TarotReading, Spread
    services.py       # AI interpretation engine
    templates/        # Tarot UI
 zodiac/                # Horoscope predictions
 tarot_project/         # Main project
    settings.py       # Configuration
    urls.py           # URL routing
 static/                # CSS, JS, images
`

---

## Installation

### Requirements
- Python 3.11+
- pip
- virtualenv
- API Keys: OpenAI, Google Gemini (or OpenRouter)

### Quick Start

`ash
# 1. Clone repository
git clone https://github.com/losing911/horoscope.git
cd horoscope

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env file:
# - OPENAI_API_KEY=your_key
# - GEMINI_API_KEY=your_key

# 5. Prepare database
python manage.py migrate
python manage.py createsuperuser

# 6. Load initial data
python manage.py populate_initial_data  # Tarot cards
python manage.py import_eprolo_products # Test products (optional)

# 7. Start server
python manage.py runserver
`

### Access
- **Homepage:** http://localhost:8000
- **Admin panel:** http://localhost:8000/admin

---

## Usage Examples

### Tarot Reading
`python
from tarot.services import TarotReadingService

service = TarotReadingService()
reading = service.create_reading(
    spread_type='celtic_cross',
    question='What about my career in next 6 months?',
    user=request.user
)
# AI-generated interpretation + card images
`

### Daily Horoscope
`python
from zodiac.services import get_daily_horoscope

horoscope = get_daily_horoscope('aries', date.today())
# Daily prediction + lucky number/color
`

### Product Revenue Analysis
`python
from shop.models import Product

product = Product.objects.get(slug='gold-ring')
revenue = product.total_revenue  # Only paid orders
quantity = product.total_sales_quantity  # Sold quantity
`

---

## Performance

### Metrics (Production)
- **Response Time:** ~200ms (with cache)
- **Tarot Interpretation:** ~3-5 seconds (AI generation)
- **Daily Active Users:** 50+ (beta)
- **Uptime:** 99.5%

### Optimizations
- Django cache (daily horoscopes)
- Gzip compression
- CDN ready for static files
- Database query optimization
- AI model fallback mechanism

---

## Security

- HTTPS with Let's Encrypt SSL
- CSRF Protection via Django middleware
- XSS Prevention through template escaping
- SQL Injection prevention with ORM
- Rate Limiting for AI endpoints
- Environment Variables for secrets
- 2FA ready admin panel

---

## Future Features

### Q1 2026
- [ ] Mobile app (React Native)
- [ ] Payment integration (Stripe/Iyzico)
- [ ] Push notifications (daily horoscope)
- [ ] Social sharing (Twitter/Instagram)

### Q2 2026
- [ ] Birth chart analysis
- [ ] Video interpretations (AI avatars)
- [ ] Premium subscription model
- [ ] Multi-language support (EN, ES, FR)

### Backlog
- [ ] WebSocket (real-time tarot)
- [ ] Blockchain NFT integration
- [ ] AR experience (tarot cards)
- [ ] Machine learning (personalization)

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (git checkout -b feature/AmazingFeature)
3. Commit changes (git commit -m 'Add some AmazingFeature')
4. Push to branch (git push origin feature/AmazingFeature)
5. Open Pull Request

### Contribution Areas
- Bug fixes
- New features
- Documentation
- Translation (i18n)
- UI/UX improvements

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Developer

**Mumin Gulay**
- Portfolio: [losing911.github.io](https://losing911.github.io)
- LinkedIn: [linkedin.com/in/mumingl](https://linkedin.com/in/mumingl)
- Email: losing911@gmail.com
- GitHub: [@losing911](https://github.com/losing911)

---

## Acknowledgments

- **OpenAI** - GPT-4o API
- **Google** - Gemini 1.5 Pro
- **Unsplash** - High-quality images
- **Django Community** - Amazing framework
- **Tarot enthusiasts** - Beta testing

---

## Contact

For questions or suggestions:

- Website: [tarot-yorum.fun](https://tarot-yorum.fun)
- Email: losing911@gmail.com
- Issues: [GitHub Issues](https://github.com/losing911/horoscope/issues)

---

<div align="center">

**Star this project if you like it!**

Made with love and magic by Mumin Gulay

</div>
