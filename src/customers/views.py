from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, TemplateView
from django.views import generic, View
from django.views.generic.edit import DeleteView, UpdateView
from .models import Customer, Address, CustomerMessage
from .forms import CustomerChangeForm, AddressForm, CustomerMessageForm
from django.urls import reverse_lazy
from django.shortcuts import redirect
import os


class CustomerProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/customers/customer_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = get_object_or_404(Customer, id=self.request.user.id)
        context['customer'] = customer
        context['address'] = customer.addresses.first()
        return context


class CustomerEditProfileView(LoginRequiredMixin, View):
    template_name = 'users/customers/customer_profile_edit.html'

    def get(self, request, *args, **kwargs):
        customer = get_object_or_404(Customer, id=request.user.id)
        form = CustomerChangeForm(instance=customer)
        return render(request, self.template_name, {
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        customer = get_object_or_404(Customer, id=request.user.id)
        form = CustomerChangeForm(instance=customer, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('customers:profile'))
        else:
            return render(request, self.template_name, {'form': form})


class CustomerDeletePhoto(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.photo:
            photo_path = user.photo.path
            if os.path.isfile(photo_path):
                os.remove(photo_path)
            user.photo = None
            user.save()
        return redirect(reverse_lazy('customers:profile-edit'))


class CustomerAddress(LoginRequiredMixin, View):
    template_name = 'users/customers/customer_profile_address.html'

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(pk=request.user.pk)
        form = AddressForm()
        addresses = customer.addresses.all()
        return render(request, self.template_name, {'form': form, 'addresses': addresses})

    def post(self, request, *args, **kwargs):
        customer = Customer.objects.get(pk=request.user.pk)
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.customer = customer
            address.save()
            form = AddressForm()
            addresses = customer.addresses.all()
            return render(request, self.template_name, {'form': form, 'addresses': addresses})
        addresses = customer.addresses.all()
        return render(request, self.template_name, {'form': form, 'addresses': addresses})


class CustomerDeleteAddressView(LoginRequiredMixin, DeleteView):
    model = Address
    template_name = 'users/customers/customer_profile_address.html'
    success_url = reverse_lazy('customers:customer-address')

    def post(self, request, *args, **kwargs):
        address_id = self.kwargs.get('pk')
        address = get_object_or_404(Address, id=address_id, customer=request.user)
        address.delete()
        return redirect(self.success_url)  # TODO No Need Post method


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    template_name = 'users/customers/customer_profile_address.html'
    form_class = AddressForm
    success_url = reverse_lazy('customers:customer-address')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['addresses'] = Address.objects.filter(customer=self.request.user)
        context['is_editing'] = True
        return context


class SendMessageCreateView(CreateView):
    model = CustomerMessageForm
    template_name = 'website/pages/contact.html'
    form_class = CustomerMessageForm
    success_url = reverse_lazy('customers:customer-send-message')

    def form_valid(self, form):
        if self.request.user.customer:
            message_instance = form.save()

            send_mail(
                subject='New Message from Customer',
                message=message_instance.message,
                from_email=self.request.user.email,
                recipient_list=['armaqanalibabaei@gmail.com'],
            )
            messages.success(self.request, "ایمیل شما ارسال شد!")
            return super().form_valid(form)
        else:
            messages.info(self.request,"فقط مشتری ها میتوانند پیام ارسال کنند.")
            return redirect('customers:customer-send-message')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['customer'] = self.request.user.customer if hasattr(self.request.user, 'customer') else None
        return kwargs
