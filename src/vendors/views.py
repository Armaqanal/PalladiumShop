from django.core.paginator import Paginator
from django.views.generic import TemplateView, DetailView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404

from .forms import VendorsChangeForm, CompanyForm, VendorForm
from .models import Vendor, Company
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views import View
from .permission_mixins import RoleBasedPermissionMixin


class VendorProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/vendors/vendor_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = get_object_or_404(Vendor, id=self.request.user.id)
        context['vendor'] = vendor
        context['company'] = vendor.company
        context['role'] = vendor.role
        return context


class VendorEditProfileView(RoleBasedPermissionMixin, View):
    template_name = 'users/vendors/vendor_profile_edit.html'
    allowed_roles = ['OWNER']
    allow_view_only = ['OPERATOR']

    def get(self, request, *args, **kwargs):
        vendor = get_object_or_404(Vendor, id=request.user.id)
        company_name = vendor.company.name if vendor.company else ''
        company_address = vendor.company.address if vendor.company else ''
        form = VendorsChangeForm(instance=vendor,
                                 initial={'company_name': company_name, 'company_address': company_address})
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


class CompaniesView(View):
    def get(self, request, *args, **kwargs):
        sales_page_number = request.GET.get('sales_page', 1)
        rate_page_number = request.GET.get('rate_page', 1)
        date_page_number = request.GET.get('newest_page', 1)

        best_companies_queryset = Company.get_best_company(limit=15)
        best_companies_rate_queryset = Company.get_best_company_rate(limit=15)
        newest_companies_queryset = Company.get_newest_companies(limit=15)

        for index, company in enumerate(best_companies_queryset):
            company.rank = index + 1

        for index, company in enumerate(best_companies_rate_queryset):
            company.rank = index + 1

        for index, company in enumerate(newest_companies_queryset):
            company.rank = index + 1

        sales_paginator = Paginator(best_companies_queryset, 4)
        rate_paginator = Paginator(best_companies_rate_queryset, 4)
        date_paginator = Paginator(newest_companies_queryset, 4)

        sales_page_obj = sales_paginator.get_page(sales_page_number)
        rate_page_obj = rate_paginator.get_page(rate_page_number)
        date_page_obj = date_paginator.get_page(date_page_number)

        context = {
            'best_companies': sales_page_obj,
            'best_companies_rate': rate_page_obj,
            'newest_companies': date_page_obj
        }

        return render(request, 'company/companies_section.html', context)


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    form_class = CompanyForm
    template_name = 'users/vendors/company_detail.html'

    def get_queryset(self):
        return Company.objects.filter(vendors=self.request.user)


class VendorsListView(RoleBasedPermissionMixin, ListView):
    model = Vendor
    form_class = VendorForm
    template_name = 'users/vendors/vendor_list.html'
    context_object_name = 'vendor_list'
    allowed_roles = ['OWNER']
    allow_view_only = ['OPERATOR', 'MANAGER']

    def get_queryset(self):
        company_id = self.kwargs.get('company_id')
        company = get_object_or_404(Company, id=company_id)
        return Vendor.objects.filter(company=company).exclude(role='OWNER')


class VendorDeleteView(RoleBasedPermissionMixin, DeleteView):
    model = Vendor
    success_url = reverse_lazy('vendors:company-list')
    template_name = 'users/vendors/vendor_list.html'
    allowed_roles = ['OWNER']
    allow_view_only = ['OPERATOR', 'MANAGER']
