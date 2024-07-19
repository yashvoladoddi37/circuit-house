import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import logging
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_session():
    session = requests.Session()
    # retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    # adapter = HTTPAdapter(max_retries=retry)
    # session.mount('http://', adapter)
    # session.mount('https://', adapter)
    return session

def get_text_safe(element):
    return element.text.strip() if element else ''

def scrape_amazon_smart_locks(base_url, num_pages=7):
    ua = UserAgent()
    session = get_session()
    products = []
    
    parsed_url = urlparse(base_url)
    base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    for page in range(1, num_pages + 1):
        page_url = f"{base_url}&page={page}" if page > 1 else base_url
        headers = {
            'User-Agent': ua.random,
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        try:
            response = session.get(page_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for product in soup.find_all('div', {'data-component-type': 's-search-result'}):
                try:
                    brand_name = get_text_safe(product.find('span', class_='a-size-base-plus'))
                    price_element = product.find('span', class_='a-price-whole')
                    price = int(price_element.text.replace(',', '')) if price_element else 0
                    rating_element = product.find('span', class_='a-icon-alt')
                    rating = float(rating_element.text.split()[0]) if rating_element else 0.0
                    rating_count_element = product.find('span', class_ = 'a-size-base s-underline-text')
                    #  {'class': 'a-size-base s-underline-text', 'dir': 'auto'}
                    rating_count = int(rating_count_element.text.replace(',', '')) if rating_count_element else 0
                    review_count = rating_count  # Assuming review count is the same as rating count
                    ranking = int(product.get('data-index', 0)) + 1
                    url_element = product.find('a', class_='a-link-normal s-no-outline')
                    url = urljoin(base_domain, url_element['href']) if url_element else ''
                    
                    if brand_name and url:  # Only add product if we have at least these two fields
                        products.append({
                            'Brand name': brand_name,
                            'Price': price,
                            'Rating': rating,
                            'Rating count': rating_count,
                            'Review count': review_count,
                            'Ranking': ranking,
                            'URL': url
                        })
                except Exception as e:
                    logging.warning(f"Error processing a product: {e}")
            
            logging.info(f"Scraped page {page}")
        except requests.RequestException as e:
            logging.error(f"Error fetching page {page}: {e}")
        
        time.sleep(random.uniform(5, 10))  # Increased delay between requests
    
    return products

def save_to_csv(products, filename='smart_locks_data.csv'):
    if not products:
        logging.warning("No products to save. CSV file will not be created.")
        return
    
    keys = products[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(products)
    logging.info(f"Data saved to {filename}")

if __name__ == "__main__":
    search_url = "https://www.amazon.in/s?k=smart+lock"
    smart_locks = scrape_amazon_smart_locks(search_url)
    
    if smart_locks:
        save_to_csv(smart_locks)
        logging.info(f"Scraped {len(smart_locks)} products and saved to CSV.")
    else:
        logging.warning("No products were scraped. Please check the search URL and try again.")