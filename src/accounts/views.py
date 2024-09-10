import random

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from customers.forms import CustomerRegisterForm, LoginForm
from customers.models import Customer
from orders.models import Order, OrderItem
from website.models import Product
from django.shortcuts import get_object_or_404

from vendors.models import Vendor
from vendors.forms import OwnerRegistrationForm, StaffRegistrationView
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.contrib.auth import login as auth_login
from django.shortcuts import redirect
from django.urls import reverse
import re
from django.core.cache import cache
from kavenegar import *

from vendors.models import Company
from vendors.permission_mixins import RoleBasedPermissionMixin

User = get_user_model()


class HomeView(TemplateView):
    template_name = 'website/pages/home.html'


class PalladiumLogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('website:product-list')


class PalladiumRegisterView(CreateView):
    model = Customer
    template_name = 'accounts/register.html'
    form_class = CustomerRegisterForm
    success_url = reverse_lazy('accounts:login')


class PalladiumOwnerRegisterView(CreateView):
    model = Vendor
    form_class = OwnerRegistrationForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/register-vendor.html'


class PalladiumLoginView(LoginView):
    template_name = 'accounts/login/index.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next_url'] = f"?{self.redirect_field_name}=" + self.request.GET.get(self.redirect_field_name, '')
        return context

    def form_valid(self, form):
        ''' bara inke form valid beshe va cooki ha ba vorod ba email az dast naran'''
        response = super().form_valid(form)
        self.handle_cart_and_order(self.request.user, response)
        return response

    def handle_cart_and_order(self, user, response):
        cart = json.loads(self.request.COOKIES.get('cart', '{}'))
        if cart:
            try:
                customer = Customer.objects.get(pk=user.pk)
                order, created = Order.objects.get_or_create(
                    customer=customer,
                    address=customer.addresses.first(),
                    state=Order.STATE.UNPAID
                )

                for product_id, quantity in cart.items():
                    product = get_object_or_404(Product, pk=product_id)
                    order_item, created = OrderItem.objects.get_or_create(
                        order=order,
                        product=product,
                        defaults={
                            'quantity': quantity,
                            'price': product.price,
                            'discounted_price': product.final_price
                        }
                    )
                    if not created:
                        order_item.quantity += quantity
                        order_item.save()

                response.delete_cookie('cart')  # TODO 2 Delete cookie
                return redirect(reverse('orders:checkout'))
            except Customer.DoesNotExist:
                return JsonResponse({'message': 'Error creating order. Please try again later.'}, status=500)

        self.login_user(self.request, user)

    def login_user(self, request, user):
        backend = 'customers.auth_backends.PalladiumBackend'
        user.backend = backend
        auth_login(request, user, backend=backend)

    def post(self, request, *args, **kwargs):
        if 'send_opt' in request.POST:
            return self.send_opt(request)
        elif 'verify_opt' in request.POST:
            return self.verify_opt(request)

        response = super().post(request, *args, **kwargs)
        response.delete_cookie('cart')
        return response

    def send_opt(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data.get('identifier')
            if identifier:
                if re.fullmatch(r'\d{10,15}', identifier):
                    opt = random.randint(100000, 999999)
                    cache_key = f"opt:{identifier}"
                    cache.set(cache_key, opt, timeout=60)
                    try:
                        api = KavenegarAPI(
                            '38746F30617070554C7974642B372F2B2F3064655A416959534B6357465871656F784746557155457A526F3D')
                        params = {
                            'receptor': identifier,
                            'message': f'{opt} تست واحد فنی'
                        }
                        response = api.sms_send(params)
                        print(f"Sending OTP {opt} to phone number {identifier}. Response: {response}")
                    except Exception as e:
                        print(f"Error sending OTP: {str(e)}")
                        return JsonResponse({'status': 'fail', 'message': 'Error sending OTP'}, status=500)

                    return JsonResponse({'status': 'opt_required', 'identifier': identifier})
                elif re.match(r'[^@]+@[^@]+\.[^@]+', identifier):
                    return JsonResponse({'status': 'email_login', 'identifier': identifier})
                return JsonResponse({'status': 'fail', 'message': 'Identifier not valid'})
        return JsonResponse({'status': 'fail', 'message': 'Form not valid'}, status=400)

    def verify_opt(self, request):
        identifier = request.POST.get('identifier')
        print(f"Received Identifier: {identifier}")

        opt = request.POST.get('opt')
        print(f"Received OTP: {opt}")

        if identifier and opt:
            cache_key = f"opt:{identifier}"
            print(f"its my cache_key opt is: {cache_key}")
            cache_opt = cache.get(cache_key)
            print(f"its my cache opt is: {cache_opt}")
            if cache_opt and str(cache_opt) == str(opt):
                cache.delete(cache_key)
                try:
                    if re.match(r'\d{10,15}', identifier):
                        user = User.objects.get(phone=identifier)
                    else:
                        user = User.objects.get(email=identifier)

                    response = JsonResponse({'status': 'success', 'redirect_url': reverse('website:product-list')})
                    self.login_user(request, user)
                    self.handle_cart_and_order(user, response)
                    return response

                except User.DoesNotExist:
                    return JsonResponse({'error': 'User does not exist'}, status=400)

            return JsonResponse({'error': 'Invalid OTP'}, status=400)
        return JsonResponse({'error': 'Required fields missing'}, status=400)


class PalladiumStaffRegistrationView(RoleBasedPermissionMixin, CreateView):
    '''
    Manager And Operator
    '''
    model = Vendor
    form_class = StaffRegistrationView
    template_name = 'users/vendors/staff_registration_form.html'
    allowed_roles = ['OWNER']

    def get_from_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.kwargs.get('company_id')
        return kwargs

    def form_valid(self, form):
        company_id = self.kwargs.get('company_id')
        company = get_object_or_404(Company, id=company_id)
        staff = form.save(commit=False)
        staff.company = company
        staff.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('website:product-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        company_id = self.kwargs.get('company_id')
        context['company'] = get_object_or_404(Company, id=company_id)
        return context
