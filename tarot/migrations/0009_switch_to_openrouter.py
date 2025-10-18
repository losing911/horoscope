# Generated manually for OpenRouter migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tarot', '0008_update_ai_providers'),
    ]

    operations = [
        # AIProvider modelini kaldır
        migrations.DeleteModel(
            name='AIProvider',
        ),
        
        # SiteSettings'den AI provider alanlarını kaldır
        migrations.RemoveField(
            model_name='sitesettings',
            name='default_ai_provider',
        ),
        migrations.RemoveField(
            model_name='sitesettings',
            name='openai_api_key',
        ),
        migrations.RemoveField(
            model_name='sitesettings',
            name='openai_model',
        ),
        migrations.RemoveField(
            model_name='sitesettings',
            name='gemini_api_key',
        ),
        migrations.RemoveField(
            model_name='sitesettings',
            name='gemini_model',
        ),
        migrations.RemoveField(
            model_name='sitesettings',
            name='ai_response_max_length',
        ),
        
        # TarotReading ve DailyCard'dan ai_provider alanını kaldır
        # (Veriyi kaybetmemek için sadece field'ı null yapıyoruz)
        migrations.AlterField(
            model_name='tarotreading',
            name='ai_provider',
            field=models.CharField(
                max_length=100,
                default='openrouter',
                verbose_name='AI Sağlayıcı',
                help_text='Artık OpenRouter kullanılıyor'
            ),
        ),
        migrations.AlterField(
            model_name='dailycard',
            name='ai_provider',
            field=models.CharField(
                max_length=100,
                default='openrouter',
                verbose_name='AI Sağlayıcı',
                help_text='Artık OpenRouter kullanılıyor'
            ),
        ),
    ]
