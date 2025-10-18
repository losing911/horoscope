"""
YouTube entegrasyonu - Kanal videolarını çekme servisi
"""
import requests
import logging
from django.conf import settings
from django.core.cache import cache
from decouple import config

logger = logging.getLogger(__name__)


class YouTubeService:
    """YouTube Data API v3 servisi"""
    
    def __init__(self):
        self.api_key = config('YOUTUBE_API_KEY', default='')
        self.channel_id = config('YOUTUBE_CHANNEL_ID', default='')
        self.base_url = 'https://www.googleapis.com/youtube/v3'
    
    def get_latest_videos(self, max_results=6):
        """
        Kanalın son videolarını getir
        
        Args:
            max_results: Kaç video getirileceği (varsayılan: 6)
        
        Returns:
            list: Video bilgileri listesi
        """
        if not self.api_key or not self.channel_id:
            logger.warning("YouTube API key veya Channel ID tanımlanmamış")
            return []
        
        # Cache kontrolü (1 saat)
        cache_key = f'youtube_videos_{self.channel_id}_{max_results}'
        cached_videos = cache.get(cache_key)
        if cached_videos:
            logger.info("YouTube videoları cache'den alındı")
            return cached_videos
        
        try:
            # YouTube API'ye istek
            url = f'{self.base_url}/search'
            params = {
                'key': self.api_key,
                'channelId': self.channel_id,
                'part': 'snippet',
                'order': 'date',
                'maxResults': max_results,
                'type': 'video'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            videos = []
            
            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                video_id = item.get('id', {}).get('videoId', '')
                
                video = {
                    'video_id': video_id,
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'published_at': snippet.get('publishedAt', ''),
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'embed_url': f'https://www.youtube.com/embed/{video_id}'
                }
                videos.append(video)
            
            # Cache'e kaydet (1 saat)
            cache.set(cache_key, videos, 3600)
            logger.info(f"{len(videos)} YouTube videosu getirildi")
            
            return videos
            
        except requests.RequestException as e:
            logger.error(f"YouTube API hatası: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"YouTube servisi hatası: {str(e)}")
            return []
    
    def get_channel_info(self):
        """Kanal bilgilerini getir"""
        if not self.api_key or not self.channel_id:
            return None
        
        cache_key = f'youtube_channel_{self.channel_id}'
        cached_info = cache.get(cache_key)
        if cached_info:
            return cached_info
        
        try:
            url = f'{self.base_url}/channels'
            params = {
                'key': self.api_key,
                'id': self.channel_id,
                'part': 'snippet,statistics'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            if items:
                item = items[0]
                snippet = item.get('snippet', {})
                statistics = item.get('statistics', {})
                
                info = {
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'subscriber_count': statistics.get('subscriberCount', '0'),
                    'video_count': statistics.get('videoCount', '0'),
                    'view_count': statistics.get('viewCount', '0'),
                    'url': f'https://www.youtube.com/channel/{self.channel_id}'
                }
                
                # Cache'e kaydet (24 saat)
                cache.set(cache_key, info, 86400)
                return info
        
        except Exception as e:
            logger.error(f"YouTube kanal bilgisi hatası: {str(e)}")
            return None
