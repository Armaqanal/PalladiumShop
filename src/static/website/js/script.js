document.addEventListener('DOMContentLoaded', function () {
    const csrftoken = getCookie('csrftoken');
    const cartIcon = document.getElementById('cart-icon');

    // Fetch initial cart quantity
    fetch('/orders/cart_quantity/')
        .then(res => res.json())
        .then(data => {
            if (data.order_quantity !== undefined && cartIcon) {
                cartIcon.setAttribute('data-notify', data.order_quantity);
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

    // Ensure buttons are loaded and exist
    const btns = document.querySelectorAll('.productContainer button');
    btns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            const product_id = e.currentTarget.getAttribute('data-product');
            const action = e.currentTarget.getAttribute('data-action');
            addToCart(product_id, action);
        });
    });

    function addToCart(product_id, action) {
        const data = {product_id: product_id, action: action};

        fetch('/orders/add/', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(data)
        })
            .then(res => {
                if (!res.ok) {
                    throw new Error('Network response was not ok');
                }
                return res.json();
            })
            .then(data => {
                if (data.order_quantity !== undefined && cartIcon) {
                    cartIcon.setAttribute('data-notify', data.order_quantity);
                }
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
