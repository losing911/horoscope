# 🔮 Tarot Yorum - AI-Powered Tarot Reading Platform

A modern, Django-based tarot reading platform with AI-powered interpretations using OpenAI and Google Gemini.

## ✨ Features

### Core Features
- **Multiple Tarot Spreads**: Single card, Three cards, Celtic Cross, Love spread, Career spread
- **AI-Powered Interpretations**: Support for OpenAI GPT and Google Gemini
- **User Management**: Registration, profiles, reading history
- **Daily Card**: Get your daily tarot guidance
- **Zodiac Integration**: Astrological signs and compatibility
- **Responsive Design**: Beautiful Bootstrap 5 interface

### Technical Features
- **Django 5.0**: Modern Python web framework
- **SQLite/PostgreSQL**: Flexible database support
- **Redis Caching**: Performance optimization
- **Security**: CSRF protection, XSS filtering, secure headers
- **Admin Panel**: Django admin for content management
- **API Ready**: JSON endpoints for mobile apps

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd tarot-python
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## 🔧 Configuration

### AI Providers

#### OpenAI Setup
1. Get API key from https://platform.openai.com/
2. Add to `.env`:
```env
OPENAI_API_KEY=sk-your-api-key
DEFAULT_AI_PROVIDER=openai
```

#### Google Gemini Setup
1. Get API key from https://makersuite.google.com/
2. Add to `.env`:
```env
GEMINI_API_KEY=your-gemini-api-key
DEFAULT_AI_PROVIDER=gemini
```

### Database Configuration

#### SQLite (Default)
```env
DATABASE_URL=sqlite:///db.sqlite3
```

#### PostgreSQL (Production)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/tarot_db
```

### Redis Caching
```env
REDIS_URL=redis://localhost:6379/1
```

## 📱 API Endpoints

### Tarot Readings
- `GET /api/spreads/` - List all tarot spreads
- `POST /api/readings/` - Create new reading
- `GET /api/readings/{id}/` - Get reading details
- `GET /api/daily-card/` - Get daily card

### User Management
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/user/profile/` - User profile
- `GET /api/user/readings/` - User's readings

## 🎨 Customization

### Adding New Tarot Spreads
1. Create spread in Django admin
2. Define positions and meanings
3. Update templates if needed

### Custom AI Prompts
Edit `ai_service.py` to customize interpretation prompts.

### Themes
Modify Bootstrap variables in `static/css/main.css`.

## 🚀 Deployment

### Heroku
```bash
# Install Heroku CLI
pip install gunicorn
git init
git add .
git commit -m "Initial commit"
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
git push heroku main
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "tarot_project.wsgi:application"]
```

### Traditional VPS
1. Install Python 3.10+, PostgreSQL, Redis
2. Clone repository and install dependencies
3. Configure environment variables
4. Set up Nginx/Apache reverse proxy
5. Use systemd for process management

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test tarot
python manage.py test accounts

# Coverage report
pip install coverage
coverage run manage.py test
coverage report
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@tarot-yorum.com
- 💬 Discord: Tarot Yorum Community
- 📝 Issues: GitHub Issues

## 🏗️ Project Structure

```
tarot-python/
├── tarot_project/          # Django project settings
├── tarot/                  # Main tarot app
├── accounts/               # User management
├── zodiac/                 # Astrology features  
├── blog/                   # Blog system
├── api/                    # REST API
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── media/                  # User uploads
├── requirements.txt        # Python dependencies
├── manage.py              # Django management
└── .env.example           # Environment template
```

## 🔮 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced astrology features
- [ ] Social features (sharing readings)
- [ ] Payment integration
- [ ] Multi-language support
- [ ] Video interpretations
- [ ] Dream journal integration

---

Made with ❤️ and ✨ by the Tarot Yorum team