from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import Order, OrderItem
from django.http import JsonResponse
from django.views import View
from customers.models import Customer, Address
from website.models import Product
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
import json
from django.db.models import Sum
from django.contrib import messages


class AddToCartView(View):
    # add products to order --->database ->Unpaid
    # add products to cart ---> cookies ->Unpaid
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))

        if request.user.is_authenticated:
            customer = get_object_or_404(Customer, pk=request.user.pk)
            order, created = Order.objects.get_or_create(customer=customer, address=customer.addresses.first(),
                                                         state=Order.STATE.UNPAID)

            product = get_object_or_404(Product, pk=product_id)
            order_item, item_created = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                defaults={'quantity': 1, 'price': product.price, 'discounted_price': product.final_price}
            )
            if not item_created:
                order_item.quantity += 1
                order_item.save()

            order_quantity = order.order_quantity
            response_data = {
                'order_quantity': order_quantity
            }
            response = JsonResponse(response_data)
        else:
            cart = json.loads(request.COOKIES.get('cart', '{}'))
            if product_id in cart:
                cart[product_id] += 1
            else:
                cart[product_id] = 1
            response_data = {
                'order_quantity': sum(cart.values()),
                'cart': cart,
                'message': 'Product added to cart'
            }
            response = JsonResponse(response_data)
            response.set_cookie('cart', json.dumps(cart))
        return response
        # TODO cart:""{\"3\": 1\054 \"2\": 1\054 \"1\": 7\054 \"4\": 1}"" encode and decode octal sequence


class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = get_object_or_404(Customer, pk=request.user.pk)
            order = Order.objects.filter(customer=customer, state=Order.STATE.UNPAID).first()
            order_items = OrderItem.objects.filter(order=order) if order else []
            addresses = Address.objects.filter(customer=customer)
            context = {
                'order': order,
                'order_items': order_items,
                'addresses': addresses,
            }
            return render(request, 'orders/order.html', context)
        else:
            return redirect('accounts:login')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = get_object_or_404(Customer, pk=request.user.pk)
            order = Order.objects.filter(customer=customer, state=Order.STATE.UNPAID).first()

            if order:
                selected_address = handle_address_selection_or_creation(request, customer, order)

                if not selected_address:
                    return redirect('orders:checkout')

                order.address = selected_address
                order.state = Order.STATE.PAID
                order.save()

                messages.success(request, "سفارش با موفقیت ثبت شد")
                return redirect('orders:checkout')
            else:
                messages.error(request, "سفارش پرداختی وجود ندارد.")
                return redirect('orders:checkout')
        else:
            return redirect('accounts:login')


class CartQuantityView(View):
    # TODO return the number of quantity for data-notify used in my ajax
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = get_object_or_404(Customer, pk=request.user.pk)
            order = Order.objects.filter(customer=customer, state=Order.STATE.UNPAID).first()
            if order:
                order_quantity = order.order_quantity
            else:
                order_quantity = 0
        else:
            cart = json.loads(request.COOKIES.get('cart', '{}'))
            order_quantity = sum(cart.values())

        response_data = {
            'order_quantity': order_quantity
        }
        return JsonResponse(response_data)


class UpdateQuantityView(View):
    # update quantity and subtotal and total cost
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        item_id = data.get('order_item_id')
        new_quantity = data.get('quantity')
        try:
            order_item = OrderItem.objects.get(id=item_id)
            order_item.quantity = new_quantity
            order_item.save()

            order = order_item.order
            order.save()

            updated_subtotal = order_item.subtotal
            updated_total_cost = order.total_cost
            return JsonResponse({'success': True, 'updated_subtotal': updated_subtotal,
                                 'updated_total_cost': updated_total_cost})
        except OrderItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'محصولی پیدا نشد'})


class DeleteOrderItemView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        item_id = data.get('order_item_id')
        try:
            order_item = OrderItem.objects.get(id=item_id)
            order = order_item.order
            order_item.delete()

            remaining_items = order.order_items.exists()
            updated_total_cost = order.order_items.aggregate(total_cost=Sum('subtotal'))['total_cost']
            updated_item_count = order.order_items.count()
            if not remaining_items:
                order.delete()

            return JsonResponse({
                'success': True,
                'updated_total_cost': updated_total_cost or 0.00,
                'updated_item_count': updated_item_count
            })
        except OrderItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'})


def handle_address_selection_or_creation(request, customer, order):
    address_id = request.POST.get('address')
    if address_id == 'new':
        address_data = request.POST.get('new_address', '')
        if address_data:
            try:
                street, city, state, zip_code = address_data.split(',', 3)
                zip_code = zip_code.strip()
                if len(zip_code) != 10:
                    messages.error(request, "کدپستی حداقل باید 10 کارکتر باشه")
                    return None
                address = Address.objects.create(
                    street=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_code=zip_code,
                    customer=customer
                )
                customer.default_address = address
                customer.save()
                return address
            except ValueError:
                messages.error(request, "لطفا با فرمت درست وارد کنید آدرس را شهر , استان , کوچه , کدپستی")
                return None
        else:
            messages.error(request, "قسمت آدرس نمیتونه خالی باشه")
            return None
    else:
        return get_object_or_404(Address, pk=address_id)

# class OrderHistoryListView(LoginRequiredMixin, ListView):
#     template_name = 'users/customers/order_history.html'
#     context_object_name = 'orders'
#
#     def get_queryset(self):
#         return Order.objects.filter(customer=self.request.user).order_by('-created_at')
#
# def get_context_data(self, **kwargs):
#     context = super().get_context_data(**kwargs)
#     context['form'] = CompanyRatingForm()
#     return context
