# 🔮 Tarot Yorum - AI-Powered Tarot & Astrology Platform# 🔮 Tarot Yorum - AI-Powered Tarot Reading Platform



A modern, Django-based tarot reading and astrology platform with AI-powered interpretations using OpenAI GPT-4o-mini.A modern, Django-based tarot reading platform with AI-powered interpretations using OpenAI and Google Gemini.



![Django](https://img.shields.io/badge/Django-5.0-green.svg)## ✨ Features

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)

![License](https://img.shields.io/badge/License-MIT-yellow.svg)### Core Features

![Status](https://img.shields.io/badge/Status-Active-success.svg)- **Multiple Tarot Spreads**: Single card, Three cards, Celtic Cross, Love spread, Career spread

- **AI-Powered Interpretations**: Support for OpenAI GPT and Google Gemini

## ✨ Key Features- **User Management**: Registration, profiles, reading history

- **Daily Card**: Get your daily tarot guidance

### 🎴 Tarot Reading System- **Zodiac Integration**: Astrological signs and compatibility

- **Multiple Spreads**: Single card, 3-card, Celtic Cross, Love, Career spreads- **Responsive Design**: Beautiful Bootstrap 5 interface

- **AI Interpretations**: Powered by OpenAI GPT-4o-mini

- **78 Tarot Cards**: Complete Major and Minor Arcana### Technical Features

- **Reading History**: Track all your readings- **Django 5.0**: Modern Python web framework

- **Daily Card**: Get daily guidance- **SQLite/PostgreSQL**: Flexible database support

- **Redis Caching**: Performance optimization

### ⭐ Zodiac & Astrology- **Security**: CSRF protection, XSS filtering, secure headers

- **12 Zodiac Signs**: Detailed personality analysis- **Admin Panel**: Django admin for content management

- **Daily Horoscopes**: AI-generated predictions- **API Ready**: JSON endpoints for mobile apps

- **Compatibility Checker**: Test zodiac compatibility

- **Lucky Factors**: Lucky days, colors, numbers## 🚀 Quick Start



### 🎨 Modern Design### Prerequisites

- **Burgundy/Cherry Theme**: Elegant dark color scheme- Python 3.10+

- **Responsive**: Mobile-first Bootstrap 5 design- pip (Python package manager)

- **Smooth Animations**: Professional hover effects

- **Clean Layout**: White card backgrounds for readability### Installation



## 🚀 Quick Start1. **Clone the repository**

```bash

```bashgit clone <repository-url>

# Clone repositorycd tarot-python

git clone https://github.com/losing911/horoscope.git```

cd horoscope

2. **Create virtual environment**

# Create virtual environment```bash

python -m venv .venvpython -m venv venv

.\.venv\Scripts\activate  # Windows# Windows

source .venv/bin/activate  # Linux/Macvenv\Scripts\activate

# macOS/Linux

# Install dependenciessource venv/bin/activate

pip install -r requirements.txt```



# Setup environment3. **Install dependencies**

cp .env.example .env```bash

# Add your OPENAI_API_KEY to .envpip install -r requirements.txt

```

# Initialize database

python manage.py migrate4. **Environment setup**

python manage.py populate_initial_data```bash

cp .env.example .env

# Create admin user# Edit .env with your configuration

python manage.py createsuperuser```



# Run server5. **Database setup**

python manage.py runserver```bash

```python manage.py makemigrations

python manage.py migrate

Visit: **http://127.0.0.1:8000/**```



## 🔧 Configuration6. **Create superuser**

```bash

Add to `.env`:python manage.py createsuperuser

```env```

SECRET_KEY=your-secret-key

DEBUG=True7. **Run development server**

OPENAI_API_KEY=sk-your-api-key```bash

OPENAI_MODEL=gpt-4o-minipython manage.py runserver

ALLOWED_HOSTS=localhost,127.0.0.1```

```

Visit: http://127.0.0.1:8000/

## 📱 Main URLs

## 🔧 Configuration

- **Home**: http://127.0.0.1:8000/

- **Tarot Spreads**: http://127.0.0.1:8000/spreads/### AI Providers

- **Zodiac Signs**: http://127.0.0.1:8000/zodiac/signs/

- **Admin Dashboard**: http://127.0.0.1:8000/dashboard/#### OpenAI Setup

- **Django Admin**: http://127.0.0.1:8000/admin/1. Get API key from https://platform.openai.com/

2. Add to `.env`:

## 🏗️ Tech Stack```env

OPENAI_API_KEY=sk-your-api-key

- **Backend**: Django 5.0.2, Python 3.10DEFAULT_AI_PROVIDER=openai

- **Database**: SQLite (upgradable to PostgreSQL)```

- **AI**: OpenAI GPT-4o-mini

- **Frontend**: Bootstrap 5.3, JavaScript#### Google Gemini Setup

- **Icons**: Font Awesome 61. Get API key from https://makersuite.google.com/

2. Add to `.env`:

## 📂 Project Structure```env

GEMINI_API_KEY=your-gemini-api-key

```DEFAULT_AI_PROVIDER=gemini

horoscope/```

├── tarot/              # Tarot reading app

├── zodiac/             # Astrology app### Database Configuration

├── accounts/           # User management

├── tarot_project/      # Django settings#### SQLite (Default)

├── templates/          # HTML templates```env

├── static/             # CSS, JS, imagesDATABASE_URL=sqlite:///db.sqlite3

└── requirements.txt    # Dependencies```

```

#### PostgreSQL (Production)

## 🎯 Commands```env

DATABASE_URL=postgresql://user:password@localhost:5432/tarot_db

```bash```

# Populate tarot cards

python manage.py populate_initial_data### Redis Caching

```env

# Generate daily horoscopesREDIS_URL=redis://localhost:6379/1

python manage.py generate_daily_horoscopes```



# Create test readings## 📱 API Endpoints

python manage.py create_fake_readings --count 50

```### Tarot Readings

- `GET /api/spreads/` - List all tarot spreads

## 🚀 Deployment- `POST /api/readings/` - Create new reading

- `GET /api/readings/{id}/` - Get reading details

### Heroku- `GET /api/daily-card/` - Get daily card

```bash

heroku create your-app-name### User Management

heroku config:set OPENAI_API_KEY=your-key- `POST /api/auth/register/` - User registration

heroku config:set SECRET_KEY=your-secret- `POST /api/auth/login/` - User login

git push heroku main- `GET /api/user/profile/` - User profile

```- `GET /api/user/readings/` - User's readings



### Docker## 🎨 Customization

```bash

docker build -t tarot-app .### Adding New Tarot Spreads

docker run -p 8000:8000 tarot-app1. Create spread in Django admin

```2. Define positions and meanings

3. Update templates if needed

## 🤝 Contributing

### Custom AI Prompts

1. Fork the repositoryEdit `ai_service.py` to customize interpretation prompts.

2. Create feature branch: `git checkout -b feature/name`

3. Commit changes: `git commit -m 'Add feature'`### Themes

4. Push: `git push origin feature/name`Modify Bootstrap variables in `static/css/main.css`.

5. Open Pull Request

## 🚀 Deployment

## 📄 License

### Heroku

MIT License - see [LICENSE](LICENSE)```bash

# Install Heroku CLI

## 🗺️ Roadmappip install gunicorn

git init

- [ ] User testimonialsgit add .

- [ ] Mobile appgit commit -m "Initial commit"

- [ ] Multi-language supportheroku create your-app-name

- [ ] Payment integrationheroku config:set SECRET_KEY=your-secret-key

- [ ] Birth chart calculatorheroku config:set DEBUG=False

git push heroku main

## 📊 Stats```



- **Files**: 99### Docker

- **Lines**: 13,000+```dockerfile

- **Languages**: Python, HTML, CSS, JavaScriptFROM python:3.11-slim

WORKDIR /app

---COPY requirements.txt .

RUN pip install -r requirements.txt

⭐ **Star this repo if you find it helpful!**COPY . .

CMD ["gunicorn", "tarot_project.wsgi:application"]

Made with ❤️ and ✨ by [@losing911](https://github.com/losing911)```


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