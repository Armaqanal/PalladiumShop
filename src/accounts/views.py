from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView,LogoutView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib import messages


from customers.forms import CustomerRegisterForm,LoginForm
from customers.models import Customer

User = get_user_model()

class PalladiumLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next_url'] = f"?{self.redirect_field_name}=" + self.request.GET.get(self.redirect_field_name, '')
        return context

    def form_valid(self, form):
        response = super(PalladiumLoginView, self).form_valid(form)
        messages.success(self.request, f"خوش آمدید '{str(self.request.user)}'")
        return response

    def form_invalid(self, form):
        for error, message in form.errors.items():
            messages.error(self.request, message)
        return super(PalladiumLoginView, self).form_invalid(form)


class PalladiumLogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('website-home')

class PalladiumRegisterView(CreateView):
    model = Customer
    template_name = 'accounts/register.html'
    form_class = CustomerRegisterForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        messages.success(self.request, f"اکانت شما با موفقیت ساخته شد")
        return super(PalladiumRegisterView, self).form_valid(form)

    def form_invalid(self, form):
        for error, message in form.errors.items():
            messages.error(self.request, message)
        return super(PalladiumRegisterView, self).form_invalid(form)