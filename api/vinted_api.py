import requests
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class VintedAPI:
    def __init__(self, country_code=".fr"):  # Changé en .fr vu tes logs
        self.country_code = country_code
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.base_url = f"https://www.vinted{country_code}"
    
    def _get_headers(self, with_auth: bool = False) -> Dict:
        headers = {
            'Host': f'www.vinted{self.country_code}',
            'x-app-version': '24.43.1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'accept-language': 'fr-FR,fr;q=0.9',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
        }

        if with_auth and self.token:
            headers['authorization'] = f'Bearer {self.token}'
            
        return headers

    def _fetch_cookies(self):
        """Simule une visite sur la page d'accueil pour récupérer les cookies anti-bot"""
        try:
            headers = self._get_headers(with_auth=False)
            self.session.get(self.base_url, headers=headers, timeout=10)
            logger.info("Cookies Vinted récupérés avec succès.")
        except Exception as e:
            logger.error(f"Impossible de récupérer les cookies: {str(e)}")
    
    async def search_products(self, search_text: str) -> List[Dict]:
        try:
            # Si on n'a pas encore de cookies, on va les chercher
            if not self.session.cookies:
                self._fetch_cookies()

            params = {
                'page': '1',
                'per_page': '10',
                'search_text': search_text,
                'order': 'newest_first',
            }
        
            # On change temporairement l'acceptation pour l'API
            headers = self._get_headers(with_auth=True)
            headers['accept'] = 'application/json'

            response = self.session.get(
                f'{self.base_url}/api/v2/catalog/items',
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            items = []
            for item in data.get('items', []):
                image_url = item.get('photos', [{}])[0].get('url', None)
                item['image_url'] = image_url
                items.append(item)
            
            return items
        except Exception as e:
            logger.error(f"Failed to search products: {str(e)}")
            return []
