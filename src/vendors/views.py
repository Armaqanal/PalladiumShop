from django.views.generic import TemplateView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404

from .forms import VendorsChangeForm
from .models import Vendor, Company
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views import View

from django.views.generic import ListView


class VendorProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/vendors/vendor_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = get_object_or_404(Vendor, id=self.request.user.id)
        context['vendor'] = vendor
        context['company'] = vendor.company
        context['role'] = vendor.role
        return context


class VendorEditProfileView(LoginRequiredMixin, View):
    template_name = 'users/vendors/vendor_profile_edit.html'

    def get(self, request, *args, **kwargs):
        vendor = get_object_or_404(Vendor, id=request.user.id)
        form = VendorsChangeForm(instance=vendor)
        return render(request, self.template_name, {
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        vendor = get_object_or_404(Vendor, id=request.user.id)
        form = VendorsChangeForm(instance=vendor, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('vendors:profile'))
        else:
            return render(request, self.template_name, {'form': form})


class BestCompany(ListView):
    model = Company
    template_name = 'company/companies_section.html'
    context_object_name = 'best_companies'
    paginate_by = 4

    def get_queryset(self):
        best_companies = Company.get_best_company(limit=15)
        for index, company in enumerate(best_companies):
            company.rank = index + 1
        return best_companies

# class RateCompanyView(LoginRequiredMixin, FormView):
#     template_name = 'users/customers/rate.html'
#     form_class = CompanyRatingForm
#
#     def dispatch(self, request, *args, **kwargs):
#         company_id = kwargs.get('company_id')
#         order_id = kwargs.get('order_id')
#
#         if not request.user.is_customer:
#             raise PermissionDenied("You do not have a customer profile.")
#
#         order = get_object_or_404(Order, id=order_id, customer=request.user)
#         company = get_object_or_404(Company, id=company_id)
#
#         if order.state != Order.STATE.PAID:
#             return redirect(reverse_lazy('customers:profile'))
#
#         return super().dispatch(request, *args, **kwargs)
#
#     def form_valid(self, form):
#         company_id = self.kwargs.get('company_id')
#         order_id = self.kwargs.get('order_id')
#
#         company = get_object_or_404(Company, id=company_id)
#         order = get_object_or_404(Order, id=order_id, customer=self.request.user)
#
#         form.instance.user = self.request.user
#         form.instance.company = company
#         form.instance.order = order
#         form.save()
#
#         messages.success(self.request, 'Your rating has been successfully submitted.')
#         return super().form_valid(form)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         company_id = self.kwargs.get('company_id')
#         order_id = self.kwargs.get('order_id')
#
#         context['company'] = get_object_or_404(Company, id=company_id)
#         context['order'] = get_object_or_404(Order, id=order_id, customer=self.request.user)
#
#         return context
#
#     def get_success_url(self):
#         return reverse_lazy('orders:order_history')
