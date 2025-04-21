let currentProducts = [];

const toggleLoader = (show) => {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = show ? 'block' : 'none';
    }
};

const showMessage = (message) => {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.textContent = message;
        messageDiv.style.display = message ? 'block' : 'none';
    }
};

const toggleSortOptions = () => {
    const sortOptions = document.getElementById('sort-options');
    if (sortOptions.style.display === 'none') {
        sortOptions.style.display = 'block';
    } else {
        sortOptions.style.display = 'none';
    }
};

const createProductCard = (product) => {
    const card = document.createElement('div');
    card.className = 'product-card';
    const title = product.title || 'N/A';
    const price = product.price ? `₹${product.price.toFixed(2)}` : 'N/A';
    const source = product.source || 'N/A';
    const stock = product.stock || 'N/A';
    const rating = product.rating && product.rating !== 'N/A' ? product.rating.toFixed(1) : 'N/A';
    const link = product.link || '#';
    const imageUrl = product.image_url || 'https://via.placeholder.com/150';

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

const displayProducts = (products) => {
    const productList = document.getElementById('product-list');
    if (!productList) {
        console.error('Product list element not found!');
        showMessage('Error: Product list element not found on the page.');
        return;
    }

    productList.innerHTML = '';
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

const sortByRating = () => {
    if (currentProducts.length > 0) {
        currentProducts.sort((a, b) => {
            const ratingA = a.rating === 'N/A' ? -Infinity : parseFloat(a.rating);
            const ratingB = b.rating === 'N/A' ? -Infinity : parseFloat(b.rating);
            return ratingB - ratingA;
        });
        displayProducts(currentProducts);
    }
    document.getElementById('sort-options').style.display = 'none';
};

const sortByPrice = () => {
    if (currentProducts.length > 0) {
        currentProducts.sort((a, b) => a.price - b.price);
        displayProducts(currentProducts);
    }
    document.getElementById('sort-options').style.display = 'none';
};

const searchProducts = async (query) => {
    toggleLoader(true);
    showMessage('');
    try {
        const url = `http://127.0.0.1:5001/api/search?q=${encodeURIComponent(query)}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const products = await response.json();

        if (products.error) throw new Error(products.error);
        if (!Array.isArray(products)) throw new Error('Invalid response format: Expected an array of products');

        currentProducts = products;
        displayProducts(products);
    } catch (error) {
        console.error('Search error:', error);
        showMessage(`Error: ${error.message}`);
    } finally {
        toggleLoader(false);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('search-input');

    if (searchButton && searchInput) {
        searchButton.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query) searchProducts(query);
            else showMessage('Please enter a search query.');
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) searchProducts(query);
                else showMessage('Please enter a search query.');
            }
        });
    } else {
        console.error('Search button or input not found!');
        showMessage('Error: Search button or input not found on the page.');
    }
});