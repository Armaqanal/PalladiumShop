from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from website.forms import CommentForm
from website.models import Product, Comment
from django.urls import reverse_lazy


class ProductListView(ListView):
    model = Product
    template_name = 'website/pages/home.html'
    context_object_name = 'products'
    queryset = Product.objects.all()
    paginate_by = 1000  # TODO


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        # context['comments'] = product.comments.approved.all()
        context['comments'] = Comment.approved.filter(product=product)
        return context


class CustomerCommentsListView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = 'customer_panel.html'
    context_object_name = 'comments'

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)


class CommentSubmissionView(LoginRequiredMixin, FormView):
    form_class = CommentForm
    template_name = 'products/product_detail.html'

    def get_success_url(self):
        return reverse_lazy('website:product-detail', kwargs={'product_id': self.kwargs['product_id']})

    def form_valid(self, form):
        product = self.get_product()
        Comment.objects.create(
            product=product,
            user=self.request.user,
            text=form.cleaned_data['text'],
            state=Comment.STATE.PENDING
        )
        return super().form_valid(form)

    def get_product(self):
        return Product.objects.get(id=self.kwargs['product_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_product()
        context['product'] = product
        context['comments'] = Comment.objects.filter(product=product, state=Comment.STATE.REGISTERED)
        context['form'] = self.get_form()
        return context
