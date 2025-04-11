// script.js

// Global variable to store the current products
let currentProducts = [];

// Function to toggle the loader (show/hide)
const toggleLoader = (show) => {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = show ? 'block' : 'none';
    }
};

// Function to show error or success messages
const showMessage = (message) => {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.textContent = message;
        messageDiv.style.display = 'block';
    }
};

// Function to create a product card
// ... (previous code remains the same until createProductCard)

const createProductCard = (product) => {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.style.border = '1px solid #ccc';
    card.style.padding = '10px';
    card.style.margin = '10px';
    card.style.width = '200px';
    card.style.display = 'inline-block';

    // Ensure all fields are safely accessed with fallbacks
    const title = product.title || 'N/A';
    const price = product.price ? `₹${product.price.toFixed(2)}` : 'N/A';
    const source = product.source || 'N/A';
    const stock = product.stock || 'N/A';
    const rating = product.rating && product.rating !== 'N/A' ? product.rating.toFixed(1) : 'N/A';
    const link = product.link || '#';
    const imageUrl = product.image_url || 'https://via.placeholder.com/150'; // Fallback image

    card.innerHTML = `
        <img src="${imageUrl}" alt="${title}" style="max-width: 100%; height: auto; margin-bottom: 10px;">
        <h3>${title}</h3>
        <p>Price: ${price}</p>
        <p>Source: ${source}</p>
        <p>Stock: ${stock}</p>
        <p>Rating: ${rating}</p>
        <a href="${link}" target="_blank">Visit Store</a>
    `;
    return card;
};

// Function to display products
const displayProducts = (products) => {
    const productList = document.getElementById('product-list');
    if (!productList) {
        console.error('Product list element not found!');
        showMessage('Error: Product list element not found on the page.');
        return;
    }

    productList.innerHTML = ''; // Clear existing products
    console.log('Displaying products:', products);

    if (!products || products.length === 0) {
        showMessage('No products found.');
        return;
    }

    products.forEach(product => {
        try {
            const card = createProductCard(product);
            productList.appendChild(card);
        } catch (error) {
            console.error('Error creating product card:', error);
            showMessage(`Error displaying product: ${error.message}`);
        }
    });
};

// Function to search products
const searchProducts = async (query) => {
    toggleLoader(true);
    showMessage(''); // Clear previous messages
    console.log(`Initiating fetch request for query: ${query}`);

    try {
        const url = `http://127.0.0.1:5001/api/search?q=${encodeURIComponent(query)}`;
        console.log(`Fetching from URL: ${url}`);

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        console.log(`Response status: ${response.status}`);
        if (!response.ok) {
            const errorData = await response.text();
            console.error('Fetch error response:', errorData);
            throw new Error(`HTTP error! Status: ${response.status}, Response: ${errorData}`);
        }

        const text = await response.text();
        console.log('Raw response text:', text);

        let products;
        try {
            products = JSON.parse(text);
        } catch (parseError) {
            console.error('Error parsing JSON:', parseError);
            throw new Error(`Failed to parse response as JSON: ${parseError.message}`);
        }

        console.log('Fetched products:', products);

        if (products.error) {
            console.error('Error in products:', products.error);
            throw new Error(products.error);
        }

        if (!Array.isArray(products)) {
            console.error('Products is not an array:', products);
            throw new Error('Invalid response format: Expected an array of products');
        }

        currentProducts = products;
        displayProducts(products);
    } catch (error) {
        console.error('Search error:', error);
        showMessage(`Error: ${error.message}`); // Only show if there's an error
    } finally {
        toggleLoader(false);
    }
};

// Event listener for the search button
document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('search-input');

    if (searchButton && searchInput) {
        searchButton.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query) {
                searchProducts(query);
            } else {
                showMessage('Please enter a search query.');
            }
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    searchProducts(query);
                } else {
                    showMessage('Please enter a search query.');
                }
            }
        });
    } else {
        console.error('Search button or input not found!');
        showMessage('Error: Search button or input not found on the page.');
    }
});