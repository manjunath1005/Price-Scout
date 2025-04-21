import logging
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class CromaScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            chrome_options.add_argument("--enable-unsafe-swiftshader")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = Service('chromedriver.exe')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("ChromeDriver initialized successfully for Croma")
        except Exception as e:
            self.logger.error(f"Error initializing ChromeDriver for Croma: {str(e)}")
            raise

    def scrape(self, query):
        try:
            search_url = f"https://www.croma.com/searchB?q={query}%3Arelevance&text={query}"
            self.logger.info(f"Scraping Croma for query: {query}, URL: {search_url}")
            self.driver.get(search_url)

            # Scroll to ensure dynamic content loads
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Wait for the product listings to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.cp-product"))
            )

            products = []
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.cp-product")
            self.logger.info(f"Found {len(product_elements)} products on Croma")

            for product in product_elements[:3]:
                try:
                    # Extract title and standardize format
                    title_elem = product.find_element(By.CSS_SELECTOR, "h3.product-title a")
                    title = title_elem.text.strip()
                    title_match = re.match(
                        r'(.+?)\s*\((\d+)GB(?:\s*RAM)?(?:,\s*(\d+)GB)?(?:,\s*(.+?))?\)',
                        title,
                        re.IGNORECASE
                    )
                    if title_match:
                        model, capacity1, capacity2, color = title_match.groups(default="Unknown")
                        capacity = capacity2 if capacity2 else capacity1
                        color = color if color else "Unknown"
                        title = f"{model} ({color}, {capacity} GB)"
                    else:
                        self.logger.warning(f"Unable to standardize title: {title}")

                    # Extract price
                    price_elem = product.find_element(By.CSS_SELECTOR, "span.amount")
                    price_text = price_elem.text.replace("₹", "").replace(",", "").strip()
                    price = float(price_text) if price_text else 0.0

                    # Extract link
                    link = title_elem.get_attribute("href")

                    # Extract rating (try alternative selectors)
                    try:
                        rating_elem = product.find_element(By.CSS_SELECTOR, "span.rating-text")
                        rating_text = rating_elem.text.strip()
                    except NoSuchElementException:
                        try:
                            rating_elem = product.find_element(By.CSS_SELECTOR, "div.rating")
                            rating_text = rating_elem.text.strip()
                        except NoSuchElementException:
                            rating_text = "N/A"
                    rating = float(rating_text) if rating_text and re.match(r'^\d+\.?\d*$', rating_text) else "N/A"

                    # Extract image URL
                    try:
                        image_elem = product.find_element(By.CSS_SELECTOR, "img")
                        image_url = image_elem.get_attribute("src")
                    except Exception as e:
                        self.logger.warning(f"Failed to extract image: {str(e)}")
                        image_url = "N/A"

                    stock = "In Stock"

                    product_data = {
                        "title": title,
                        "price": price,
                        "source": "Croma",
                        "link": link,
                        "stock": stock,
                        "rating": rating,
                        "image_url": image_url
                    }
                    products.append(product_data)
                    self.logger.debug(f"Scraped product: {product_data}")
                except Exception as e:
                    self.logger.warning(f"Error scraping Croma product: {str(e)}")
                    continue

            return products
        except Exception as e:
            self.logger.error(f"Error scraping Croma: {str(e)}")
            return []
        finally:
            time.sleep(1)

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("ChromeDriver closed successfully for Croma")
            except Exception as e:
                self.logger.warning(f"Error closing ChromeDriver for Croma: {str(e)}")
            finally:
                self.driver = None

class AmazonScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            chrome_options.add_argument("--enable-unsafe-swiftshader")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = Service('chromedriver.exe')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("ChromeDriver initialized successfully for Amazon")
        except Exception as e:
            self.logger.error(f"Error initializing ChromeDriver for Amazon: {str(e)}")
            raise

    def scrape(self, query):
        try:
            search_url = f"https://www.amazon.in/s?k={query}"
            self.logger.info(f"Scraping Amazon for query: {query}, URL: {search_url}")
            self.driver.get(search_url)

            # Scroll to ensure dynamic content loads
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Wait for the product listings to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']"))
            )

            products = []
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
            self.logger.info(f"Found {len(product_elements)} products on Amazon")

            for product in product_elements[:3]:
                try:
                    # Extract title with cleaning and formatting
                    try:
                        title_elem = product.find_element(By.CSS_SELECTOR, "h2.a-size-medium.a-color-base.a-text-normal span")
                        raw_title = title_elem.text.strip()
                        clean_title = re.sub(r'_\w+\s*\w+$', '', raw_title).strip()
                        if not clean_title or clean_title == raw_title:
                            h2_elem = product.find_element(By.CSS_SELECTOR, "h2.a-size-medium.a-color-base.a-text-normal")
                            aria_label = h2_elem.get_attribute("aria-label")
                            title = aria_label if aria_label else raw_title
                        else:
                            title = clean_title
                        title_match = re.match(
                            r'(.+?)\s*\((\d+)GB(?:,\s*(\w+))?\)',
                            title,
                            re.IGNORECASE
                        )
                        if title_match:
                            model, capacity, color = title_match.groups(default="Unknown")
                            title = f"{model} ({color}, {capacity} GB)"
                        if "Sponsored Ad" in title or ("aria-label" in locals() and "Sponsored Ad" in aria_label):
                            self.logger.debug("Skipping sponsored product")
                            continue
                        self.logger.debug(f"Extracted title: {title}")
                    except Exception as e:
                        self.logger.warning(f"Failed to extract title: {str(e)}")
                        title = "N/A"
                        continue

                    # Extract price (with fallback)
                    try:
                        price_elem = product.find_element(By.CSS_SELECTOR, "span.a-price-whole")
                        price_text = price_elem.text.replace(",", "").strip()
                        if not price_text:
                            price_elem = product.find_element(By.CSS_SELECTOR, "span.a-offscreen")
                            price_text = price_elem.text.replace("₹", "").replace(",", "").strip()
                        price = float(price_text) if price_text else 0.0
                    except Exception as e:
                        self.logger.warning(f"Failed to extract price: {str(e)}")
                        price = 0.0

                    # Extract link
                    try:
                        link_elem = product.find_element(By.CSS_SELECTOR, "a.a-link-normal.s-no-outline")
                        link = link_elem.get_attribute("href")
                    except Exception as e:
                        self.logger.warning(f"Failed to extract link: {str(e)}")
                        link = "N/A"

                    # Extract rating
                    try:
                        rating_elem = product.find_element(By.CSS_SELECTOR, "a.a-popover-trigger.a-declarative")
                        aria_label = rating_elem.get_attribute("aria-label")
                        rating_text = re.search(r'(\d+\.\d+)\s+out\s+of\s+5\s+stars', aria_label)
                        rating = float(rating_text.group(1)) if rating_text else "N/A"
                    except Exception as e:
                        self.logger.warning(f"Failed to extract rating: {str(e)}")
                        rating = "N/A"

                    # Extract image URL
                    try:
                        image_elem = product.find_element(By.CSS_SELECTOR, "img.s-image")
                        image_url = image_elem.get_attribute("src")
                    except Exception as e:
                        self.logger.warning(f"Failed to extract image: {str(e)}")
                        image_url = "N/A"

                    stock = "In Stock"

                    product_data = {
                        "title": title,
                        "price": price,
                        "source": "Amazon",
                        "link": link,
                        "stock": stock,
                        "rating": rating,
                        "image_url": image_url
                    }
                    products.append(product_data)
                    self.logger.debug(f"Scraped product: {product_data}")
                except Exception as e:
                    self.logger.warning(f"Error scraping Amazon product: {str(e)}")
                    continue

            return products
        except Exception as e:
            self.logger.error(f"Error scraping Amazon: {str(e)}")
            return []
        finally:
            time.sleep(1)

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("ChromeDriver closed successfully for Amazon")
            except Exception as e:
                self.logger.warning(f"Error closing ChromeDriver for Amazon: {str(e)}")
            finally:
                self.driver = None

class FlipkartScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            chrome_options.add_argument("--enable-unsafe-swiftshader")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = Service('chromedriver.exe')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("ChromeDriver initialized successfully for Flipkart")
        except Exception as e:
            self.logger.error(f"Error initializing ChromeDriver for Flipkart: {str(e)}")
            raise

    def scrape(self, query):
        try:
            search_url = f"https://www.flipkart.com/search?q={query}"
            self.logger.info(f"Scraping Flipkart for query: {query}, URL: {search_url}")
            self.driver.get(search_url)

            # Scroll to ensure dynamic content loads
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Wait for the product listings to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-id]"))
            )

            products = []
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-id]")
            self.logger.info(f"Found {len(product_elements)} products on Flipkart")

            for product in product_elements[:3]:
                try:
                    # Extract title
                    try:
                        title_elem = product.find_element(By.CSS_SELECTOR, "div.KzDlHZ")
                        title = title_elem.text.strip()
                    except:
                        title = "N/A"

                    # Extract price
                    try:
                        price_elem = product.find_element(By.CSS_SELECTOR, "div.Nx9bqj._4b5DiR")
                        price_text = price_elem.text.replace("₹", "").replace(",", "").strip()
                        price = float(price_text) if price_text else 0.0
                    except:
                        price = 0.0

                    # Extract link
                    try:
                        link_elem = product.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                        link = link_elem.get_attribute("href")
                    except:
                        link = "N/A"

                    # Extract rating
                    try:
                        rating_elem = product.find_element(By.CSS_SELECTOR, "div.XQDdHH")
                        rating_text = rating_elem.text.strip()
                        rating = float(rating_text) if rating_text else "N/A"
                    except:
                        rating = "N/A"

                    # Extract image URL
                    try:
                        image_elem = product.find_element(By.CSS_SELECTOR, "img.DByuf4")
                        image_url = image_elem.get_attribute("src")
                    except Exception as e:
                        self.logger.warning(f"Failed to extract image: {str(e)}")
                        image_url = "N/A"

                    stock = "In Stock"

                    product_data = {
                        "title": title,
                        "price": price,
                        "source": "Flipkart",
                        "link": link,
                        "stock": stock,
                        "rating": rating,
                        "image_url": image_url
                    }
                    products.append(product_data)
                    self.logger.debug(f"Scraped product: {product_data}")
                except Exception as e:
                    self.logger.warning(f"Error scraping Flipkart product: {str(e)}")
                    continue

            return products
        except Exception as e:
            self.logger.error(f"Error scraping Flipkart: {str(e)}")
            return []
        finally:
            time.sleep(1)

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("ChromeDriver closed successfully for Flipkart")
            except Exception as e:
                self.logger.warning(f"Error closing ChromeDriver for Flipkart: {str(e)}")
            finally:
                self.driver = None