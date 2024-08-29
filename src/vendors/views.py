from django.core.paginator import Paginator
from django.views.generic import TemplateView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404

from .forms import VendorsChangeForm
from .models import Vendor, Company
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views import View


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


# class BestCompany(ListView):
#     '''
#     Based on sales
#     '''
#     model = Company
#     template_name = 'company/companies_section.html'
#     context_object_name = 'best_companies'
#     paginate_by = 4
#
#     def get_queryset(self):
#         best_companies = Company.get_best_company(limit=15)
#         for index, company in enumerate(best_companies):
#             company.rank = index + 1
#         return best_companies
#
#
# class BestCompanyRate(ListView):
#     '''
#     Based on Rate
#     '''
#     model = Company
#     template_name = 'company/companies_section.html'
#     context_object_name = 'best_companies_rate'
#     paginate_by = 4
#
#     def get_queryset(self):
#         best_companies_rate = Company.get_best_company_rate(limit=15)
#         for index, company in enumerate(best_companies_rate):
#             company.rank = index + 1
#         return best_companies_rate


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
