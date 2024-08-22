from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404

from .forms import VendorsChangeForm
from .models import Vendor
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
