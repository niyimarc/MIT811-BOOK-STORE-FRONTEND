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
            Toastify({
                text: "✅ Added to cart!",
                duration: 4000,
                gravity: "bottom", // top or bottom
                position: "right", // left, center, or right
                backgroundColor: "#2ecc71",
            }).showToast();

            // Delay reload until toast disappears
            setTimeout(() => {
                location.reload();
            }, 3100);
        } else {
            Toastify({
                text: "❌ Failed to add: " + (result.error || "Unknown error"),
                duration: 4000,
                gravity: "bottom",
                position: "right",
                backgroundColor: "#e74c3c",
            }).showToast();
        }
    })
    .catch(error => {
        console.error("Add to cart failed:", error);
        Toastify({
            text: "⚠️ Something went wrong.",
            duration: 4000,
            gravity: "bottom",
            position: "right",
            backgroundColor: "#e74c3c",
        }).showToast();
    });
}
