document.addEventListener('DOMContentLoaded', function () {
    const csrftoken = getCookie('csrftoken');
    const cartIcon = $('#cart-icon');

    $.ajax({
        url: '/orders/cart_quantity/',
        type: 'GET',
        success: function (data) {
            if (data.order_quantity !== undefined && cartIcon) {
                cartIcon.attr('data-notify', data.order_quantity);
            }
        },
        error: function (xhr, status, error) {
            console.error('There was a problem with the AJAX operation:', error);
        }
    });

    $('.productContainer button').on('click', function (e) {
        const product_id = $(this).data('product');
        const action = $(this).data('action');
        addToCart(product_id, action);
    });

    function addToCart(product_id, action) {
        $.ajax({
            url: '/orders/add/',
            type: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            data: JSON.stringify({product_id: product_id, action: action}),
            contentType: 'application/json',
            success: function (data) {
                if (data.order_quantity !== undefined && cartIcon) {
                    cartIcon.attr('data-notify', data.order_quantity);
                }
            },
            error: function (xhr, status, error) {
                console.error('There was a problem with the AJAX operation:', error);
            }
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
