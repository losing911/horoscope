# -*- coding: utf-8 -*-
# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tarot', '0007_alter_sitesettings_default_ai_provider_and_more'),
    ]

    operations = [
        # AIProvider modelini güncelle
        migrations.AddField(
            model_name='aiprovider',
            name='provider_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('openai', 'OpenAI'),
                    ('gemini', 'Google Gemini'),
                    ('deepseek', 'DeepSeek'),
                ],
                default='openai',
                verbose_name="Sağlayıcı Türü"
            ),
        ),
        migrations.AddField(
            model_name='aiprovider',
            name='model_name',
            field=models.CharField(
                max_length=100,
                default='gpt-4o-mini',
                verbose_name="Model Adı"
            ),
        ),
        migrations.AddField(
            model_name='aiprovider',
            name='is_default',
            field=models.BooleanField(
                default=False,
                verbose_name="Varsayılan Sağlayıcı"
            ),
        ),
        migrations.AddField(
            model_name='aiprovider',
            name='priority',
            field=models.IntegerField(
                default=1,
                verbose_name="Öncelik"
            ),
        ),
        migrations.AddField(
            model_name='aiprovider',
            name='base_url',
            field=models.URLField(
                blank=True,
                verbose_name="API Base URL"
            ),
        ),
    ]