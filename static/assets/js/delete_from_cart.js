function deleteCartItem(productId) {
    fetch(`/remove_cart/${productId}/`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Item removed from cart");
            location.reload();
        } else {
            alert("Error: " + (data.error || "Unable to remove item"));
        }
    })
    .catch(err => {
        console.error("Delete error", err);
        alert("Unexpected error occurred");
    });
}
