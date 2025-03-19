import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import time
import re

class NeweggAPI:
    def __init__(self):
        self.base_url = "https://www.newegg.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        self.session = requests.Session()
        self.rate_limit_delay = 1  # Delay between requests in seconds

    def _extract_price(self, price_text: str) -> float:
        """Extract numeric price from string"""
        if not price_text:
            return 0.0
        price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
        if price_match:
            return float(price_match.group(1).replace(',', ''))
        return 0.0

    def _parse_product(self, item: BeautifulSoup) -> Dict:
        """Parse product information from HTML"""
        try:
            title_elem = item.find('a', class_='item-title')
            price_elem = item.find('li', class_='price-current')
            
            return {
                'title': title_elem.text.strip() if title_elem else '',
                'url': f"{self.base_url}{title_elem['href']}" if title_elem else '',
                'price': self._extract_price(price_elem.text if price_elem else ''),
                'rating': item.find('a', class_='item-rating')['title'] if item.find('a', class_='item-rating') else None,
                'store': 'Newegg'
            }
        except Exception as e:
            print(f"Error parsing product: {e}")
            return {}

    def search(self, keyword: str, sort: str = 'price-low-to-high', 
               price_from: float = 0, price_to: float = None, limit: int = 5) -> List[Dict]:
        """
        Search Newegg for products matching the criteria
        """
        try:
            # Build search URL
            url = f"{self.base_url}/p/pl?d={keyword}"
            if sort == 'price-low-to-high':
                url += "&Order=1"
            if price_from or price_to:
                url += f"&Price={int(price_from)}"
                if price_to:
                    url += f"-{int(price_to)}"

            # Make request
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')
            items = soup.find_all('div', class_='item-cell')
            
            # Extract product information
            products = []
            for item in items[:limit]:
                product = self._parse_product(item)
                if product:
                    products.append(product)
                
            time.sleep(self.rate_limit_delay)  # Rate limiting
            return products
            
        except requests.RequestException as e:
            print(f"Error searching Newegg: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []