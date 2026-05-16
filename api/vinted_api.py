import requests
import logging
import random
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class VintedAPI:
    def __init__(self, country_code=".fr"):
        self.country_code = country_code
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.base_url = f"https://www.vinted{country_code}"
    
    def _get_headers(self) -> Dict:
        # On imite parfaitement l'application mobile officielle de Vinted
        return {
            'Host': f'www.vinted{self.country_code}',
            'x-app-version': '24.43.1',
            'accept': 'application/json',
            'accept-language': 'fr-FR,fr;q=0.9',
            'user-agent': 'vinted-ios Vinted/24.43.1 (lt.manodrabuziai.fr; build:30115; iOS 17.5) iPhone14,3',
            'x-device-model': 'iPhone14,3',
            'connection': 'keep-alive'
        }

    def _fetch_cookies(self):
        """Simule l'ouverture de l'application pour choper les cookies"""
        try:
            headers = self._get_headers()
            # On va sur la page d'accueil d'abord
            self.session.get(self.base_url, headers=headers, timeout=10)
            logger.info("Cookies de session mobiles récupérés.")
        except Exception as e:
            logger.error(f"Erreur cookies: {str(e)}")
    
    async def search_products(self, search_text: str) -> List[Dict]:
        try:
            if not self.session.cookies:
                self._fetch_cookies()

            # Paramètres officiels de l'application mobile
            params = {
                'search_text': search_text,
                'page': '1',
                'per_page': '20',
                'order': 'newest_first',
            }
        
            headers = self._get_headers()

            # Requête vers l'API de recherche
            response = self.session.get(
                f'{self.base_url}/api/v2/catalog/items',
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 403:
                logger.error("Vinted bloque toujours l'IP de ton serveur Render (403).")
                return []
                
            response.raise_for_status()
            data = response.json()
            
            items = []
            for item in data.get('items', []):
                image_url = item.get('photos', [{}])[0].get('url', None)
                item['image_url'] = image_url
                items.append(item)
            
            return items
        except Exception as e:
            logger.error(f"Erreur recherche: {str(e)}")
            return []
