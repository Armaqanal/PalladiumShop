from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from customers.forms import CustomerRegisterForm, LoginForm
from customers.models import Customer
from orders.models import Order, OrderItem
from website.models import Product
from django.shortcuts import get_object_or_404

from vendors.models import Vendor
from vendors.forms import OwnerRegistrationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
import json

User = get_user_model()


class HomeView(TemplateView):
    template_name = 'website/pages/home.html'


class PalladiumLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next_url'] = f"?{self.redirect_field_name}=" + self.request.GET.get(self.redirect_field_name, '')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        cart = json.loads(self.request.COOKIES.get('cart', '{}'))
        if cart:
            try:
                customer = Customer.objects.get(pk=self.request.user.pk)
                order = Order.objects.create(customer=customer,address=customer.addresses.first(), state=Order.STATE.UNPAID)
                for product_id, quantity in cart.items():
                    product = get_object_or_404(Product, pk=product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price,
                        discounted_price=product.final_price
                    )
                response.delete_cookie('cart')
            except ObjectDoesNotExist:
                return JsonResponse({'message': 'Error creating order. Please try again later.'}, status=500)

        auth_login(self.request, self.request.user)
        return response


class PalladiumLogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('accounts:home')
    # next_page = redirect('/')


class PalladiumRegisterView(CreateView):
    model = Customer
    template_name = 'accounts/register.html'
    form_class = CustomerRegisterForm
    success_url = reverse_lazy('accounts:login')


class PalladiumOwnerRegisterView(CreateView):
    # chera ba formView nemishe
    model = Vendor
    form_class = OwnerRegistrationForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/register-vendor.html'

