import re
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup basic logging for information and debugging purposes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver(headless=True):
    """Set up the Selenium WebDriver with specified options for browsing."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")  # Disables GPU hardware acceleration
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--window-size=1920,1080")  # Set browser window size
    chrome_options.headless = headless  # Run browser in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)   

    if headless:
            chrome_options.add_argument("--headless")  # Run browser in headless mode
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver



def scroll_to_bottom(driver):
    """Scrolls to the bottom of a webpage to ensure all dynamic content is loaded."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Allow time for page to load after scrolling
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        

def clean_text(text):
    """Cleans text by removing excessive whitespace and unwanted characters."""
    return re.sub(r'\s+', ' ', text).strip()

def get_product_data(url, search_query, config):
    """Navigate to a URL, perform a search, and collect product data based on provided configurations."""
    driver = setup_driver()  # Set headless to True for production
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, config['search_input_selector']))
        )
        logging.info("Search input is visible.")
        
        search_input = driver.find_element(By.CSS_SELECTOR, config['search_input_selector'])
        search_input.clear()
        search_input.send_keys(search_query + Keys.ENTER)
        logging.info("Search query submitted.")

        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, config['product_list_selector']))
        )
        logging.info("Products are visible.")
        
        scroll_to_bottom(driver)
        return parse_products(driver, config)
    finally:
        driver.quit()

def parse_products(driver, config):
    """Parse the product information from the page using the provided driver and config."""
    products = []
    product_cards = driver.find_elements(By.CSS_SELECTOR, config['product_list_selector'])
    for card in product_cards:
        name = card.find_element(By.CSS_SELECTOR, config['name_selector']).text.strip() if card.find_elements(By.CSS_SELECTOR, config['name_selector']) else 'No Name'
        price = card.find_element(By.CSS_SELECTOR, config['price_selector']).text.strip() if card.find_elements(By.CSS_SELECTOR, config['price_selector']) else 'No Price'
        link = card.find_element(By.CSS_SELECTOR, config['link_selector']).get_attribute('href') if card.find_elements(By.CSS_SELECTOR, config['link_selector']) else '#'
        full_link = config['base_url'] + link
        products.append({'name': name, 'price': price, 'details': full_link})
        logging.info(f"Captured: {name}, {price}, {full_link}")
    return products

configs = {
    
    'supermercadoA': {
        'base_url': "https://loja.supermercadosavenida.com.br",
        'product_list_selector': 'ul.product-grid > li',
        'name_selector': 'div.product-card-name-container',
        'price_selector': 'span.new-price',
        'link_selector': 'a',
        'search_input_selector': 'input[name="search"]',
        'results_container_selector': '.product-listing__results',
    },
    'supermercadoC': {
        'base_url': "https://www.sitemercado.com.br/supermercadolavilla/ourinhos-loja-ourinhos-jardim-matilde-r-do-expedicionario/",
        'product_list_selector': 'div.list-product-item',
        'name_selector': '.txt-desc-product-itemtext-muted.txt-desc-product-item',
        'price_selector': '.area-bloco-preco.bloco-preco.pr-0.ng-star-inserted',
        'link_selector': 'a.list-product-link',
        'search_input_selector': 'input[name="search"]',
        'results_container_selector': 'div.list-product-item',
    },
    
}

# Example usage (For testing purposes)
if __name__ == "__main__":
    results = get_product_data(configs['supermercadoC']['base_url'], 'energetico', configs['supermercadoC'])
    for product in results:
        print(f"Name: {product['name']}, Price: {product['price']}, Details: {product['details']}")
    results2 = get_product_data(configs['supermercadoA']['base_url'], 'energetico', configs['supermercadoA'])
    for product in results2:
        print(f"Name: {product['name']}, Price: {product['price']}, Details: {product['details']}")