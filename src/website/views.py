from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from website.forms import CommentForm, ProductForm, ProductImageForm
from website.models import Product, Comment, Category, ProductImage
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from vendors.models import Company
from .forms import DiscountForm
import json
from django.http import JsonResponse


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

    def post(self, request, *args, **kwargs):
        cart = json.loads(request.COOKIES.get('cart', '{}'))
        product_id = request.POST['product_id']
        if product_id in cart:
            cart[product_id] += 1
        else:
            cart[product_id] = 1
        response = JsonResponse({'message': 'محصول به سبد خرید اضافه شد'})
        response.set_cookie('cart', json.dumps(cart))
        return response


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_create_view.html'
    extra_context = {'action_type': 'Adding'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['discount'] = DiscountForm(self.request.POST)
            context['images_form'] = ProductImageForm(self.request.POST, self.request.FILES)
        else:
            context['discount'] = DiscountForm()
            context['images_form'] = ProductImageForm()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        discount = context['discount']
        images_form = context['images_form']

        try:
            company = Company.objects.get(vendors=self.request.user)
        except Company.DoesNotExist:
            form.add_error(None, "No company found for this vendor.")
            return self.form_invalid(form)

        if form.is_valid() and discount.is_valid() and images_form.is_valid():
            form.instance.vendor = self.request.user
            form.instance.company = company
            self.object = form.save()

            discount.instance = self.object
            discount.save()

            images = self.request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(product=self.object, image=image)

            return super().form_valid(form)
        else:
            return self.form_invalid(form)


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
        return reverse_lazy('website:product-detail', kwargs={'slug': self.kwargs['slug']})

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
        return get_object_or_404(Product, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_product()
        context['product'] = product
        context['comments'] = Comment.objects.filter(product=product, state=Comment.STATE.REGISTERED)
        context['form'] = self.get_form()
        return context


class CategoryListView(ListView):
    context_object_name = "main-category"
    template_name = 'website/sections/category.html'

    def get_queryset(self):
        parents = Category.objects.filter(subcategories__isnull=None)
        return parents


class SubCategoryListView(ListView):
    context_object_name = "sub-category"
    template_name = 'website/sections/category.html'

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return Category.objects.filter(subcategories__id=category_id)
