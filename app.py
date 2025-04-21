import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from scraper import FlipkartScraper, AmazonScraper, CromaScraper  # Import all scraper classes
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def is_relevant_product(product, query):
    """Check if the product title is relevant to the query."""
    if not product or 'title' not in product:
        return False
    title = product['title'].lower()
    query_terms = query.lower().split()
    return all(term in title for term in query_terms)

@app.route('/')
def index():
    logger.debug("Serving index.html")
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def api_search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    logger.info(f"Received search query: {query}")
    products = []

    # Initialize all scrapers
    croma_scraper = CromaScraper()
    amazon_scraper = AmazonScraper()
    flipkart_scraper = FlipkartScraper()

    try:
        # Scrape in the specified order: Flipkart first, Amazon second, Croma last
        flipkart_products = flipkart_scraper.scrape(query)
        filtered_flipkart_products = [p for p in flipkart_products if is_relevant_product(p, query)]
        if filtered_flipkart_products:  # Only extend if there are relevant products
            products.extend(filtered_flipkart_products)
            logger.debug(f"Added {len(filtered_flipkart_products)} relevant Flipkart products")

        amazon_products = amazon_scraper.scrape(query)
        filtered_amazon_products = [p for p in amazon_products if is_relevant_product(p, query)]
        if filtered_amazon_products:  # Only extend if there are relevant products
            products.extend(filtered_amazon_products)
            logger.debug(f"Added {len(filtered_amazon_products)} relevant Amazon products")

        croma_products = croma_scraper.scrape(query)
        filtered_croma_products = [p for p in croma_products if is_relevant_product(p, query)]
        if filtered_croma_products:  # Only extend if there are relevant products
            products.extend(filtered_croma_products)
            logger.debug(f"Added {len(filtered_croma_products)} relevant Croma products")

        logger.info(f"Returning {len(products)} relevant products for query: {query} from active platforms")
        return jsonify(products)
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        croma_scraper.close()
        amazon_scraper.close()
        flipkart_scraper.close()

if __name__ == '__main__':
    logger.info("Starting Flask server on http://127.0.0.1:5001")
    app.run(debug=True, port=5001)