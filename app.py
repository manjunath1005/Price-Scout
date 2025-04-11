import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from scraper import CromaScraper, AmazonScraper, FlipkartScraper  # Import all scraper classes

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

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
        # Scrape from Croma
        croma_products = croma_scraper.scrape(query)
        products.extend(croma_products)

        # Scrape from Amazon
        amazon_products = amazon_scraper.scrape(query)
        products.extend(amazon_products)

        # Scrape from Flipkart
        flipkart_products = flipkart_scraper.scrape(query)
        products.extend(flipkart_products)

        logger.info(f"Returning {len(products)} products for query: {query}")
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