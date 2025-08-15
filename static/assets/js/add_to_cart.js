function addToCart(productId) {
    const qtyInput = document.querySelector(`#qty-${productId}`);
    let quantity = parseInt(qtyInput?.value) || 1;
    
    const cartItem = {
        product_id: productId,
        quantity: quantity
    };

    fetch(addToCartUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(cartItem),
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Added to cart!');
            location.reload();
            // getCartDetails?.(); 
        } else {
            alert('Failed to add to cart: ' + (result.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Add to cart failed:', error);
        alert('Something went wrong.');
    });
}
