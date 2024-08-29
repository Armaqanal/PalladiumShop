import json

from django.db.models import Sum
from django.http import JsonResponse
from django.views import View
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
from vendors.models import Company, Vendor
from .forms import DiscountForm, ProductRatingForm
from django.contrib import messages

from orders.models import Order
import logging

from .models import ProductRating


class ProductListView(ListView):
    model = Product
    template_name = 'website/pages/home.html'
    context_object_name = 'products'
    paginate_by = 1000

    def get_queryset(self):
        products = Product.objects.all()
        search = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        company = self.request.GET.get('company', '')

        if search:
            products = products.filter(name__icontains=search) | products.filter(slug__icontains=search)
        if category:
            products = products.filter(category__name=category)
        if company:
            products = products.filter(company__name__icontains=company)
        products = self.filtered_by_product_rate(products)
        products = self.filtered_by_product_price(products)
        products = self.filtered_by_product_best_sales(products)

        return products

    def filtered_by_product_rate(self, products):
        product_rate = self.request.GET.get('rate', '')
        if product_rate:
            try:
                products_rate = float(product_rate)
                if not 1.0 <= products_rate <= 5.0:
                    messages.error(self.request, "لطفا بین 1-5 انتخاب کنید")
                else:
                    products = products.filter(average_rating__gte=products_rate)
                    messages.success(self.request, "شما در حال تماشای محبوب ترین ها هستید")
            except ValueError:
                messages.error(self.request, "رتبه محصول نامعتبر هست")
        return products

    def filtered_by_product_price(self, products):
        product_price = self.request.GET.get('pricey', '')
        if product_price:
            products = products.order_by('-price')[:6]
        return products

    def filtered_by_product_best_sales(self, products):
        product_sales = self.request.GET.get('best_sales', '')
        if product_sales:
            products = products.annotate(total_quantity=Sum('order_items__quantity')).filter(
                order_items__order__state=Order.STATE.PAID).order_by('-total_quantity')[:5]
            messages.success(self.request, "شما در حال تماشای پرفروش ترین ها هستید")
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['companies'] = Company.objects.all()

        company_name = self.request.GET.get('company', '')
        if company_name:
            try:
                context['filtered_company'] = Company.objects.get(name__icontains=company_name)
            except Company.DoesNotExist:
                context['filtered_company'] = None
        return context


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

            images = self.request.FILES.getlist('image')
            for image in images:
                ProductImage.objects.create(product=self.object, image=image)

            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_update.html'
    extra_context = {'action_type': 'Editing'}

    def get_queryset(self):
        vendor = self.request.user.vendor
        company = vendor.company
        return Product.objects.filter(company=company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['discount'] = DiscountForm(self.request.POST, instance=self.object.discount)
            context['images_form'] = ProductImageForm(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['discount'] = DiscountForm(instance=self.object.discount)
            context['images_form'] = ProductImageForm(instance=self.object)
            context['existing_images'] = ProductImage.objects.filter(product=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        discount = context['discount']
        images_form = context['images_form']
        if form.is_valid() and discount.is_valid() and images_form.is_valid():
            self.object = form.save()
            discount.save()
            images_to_delete = self.request.POST.getlist('delete_images')
            if images_to_delete:
                ProductImage.objects.filter(id__in=images_to_delete).delete()
            new_images = self.request.FILES.getlist('image')
            for image in new_images:
                ProductImage.objects.create(product=self.object, image=image)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('website:product-summary')
    template_name = 'products/product_table.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        ProductImage.objects.filter(product=self.object).delete()
        if self.object.discount:
            self.object.discount.delete()
        return super().delete(request, *args, **kwargs)


class ProductSummaryListView(ListView):
    model = Product
    template_name = 'products/product_table.html'
    context_object_name = 'products'

    def get_queryset(self):
        vendor = self.request.user.vendor
        company = vendor.company
        return Product.objects.filter(company=company)


class CustomerCommentsListView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = 'users/customers/comments_section.html'
    context_object_name = 'comments'

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['total_comments'] = self.get_queryset().count()
        return context


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    success_url = reverse_lazy('website:comment-list')
    template_name = 'users/customers/comments_section.html'

    def form_valid(self, form):
        messages.success(self.request, 'کامنت با موفقیت حذف شد')
        return super().form_valid(form)


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
    model = Category
    context_object_name = "main_categories"
    template_name = 'website/sections/category_section.html'

    def get_queryset(self):
        queryset = Category.objects.filter(subcategories__isnull=True).prefetch_related('parent_categories')
        return queryset


class SubCategoryListView(ListView):
    context_object_name = "sub_categories"
    template_name = 'website/sections/category_section.html'

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        main_category = get_object_or_404(Category, id=category_id)
        queryset = Category.objects.filter(subcategories=main_category)
        return queryset


class CheckPurchaseView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        print(f"CheckPurchaseView: Received product_id: {product_id}")

        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        if not product_id:
            print("CheckPurchaseView: product_id is None or empty")
            return JsonResponse({'error': 'Invalid product_id'}, status=400)

        product = get_object_or_404(Product, pk=product_id)
        print(f"CheckPurchaseView: Found product: {product}")

        has_paid_order = Order.objects.filter(
            customer=user.customer,
            state=Order.STATE.PAID,
            order_items__product=product
        ).exists()
        print(f"CheckPurchaseView: Has paid order: {has_paid_order}")

        return JsonResponse({'has_purchased': has_paid_order})


class RateProductView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        rating_value = data.get('rating')

        print(f"RateProductView: Received product_id: {product_id}")
        print(f"RateProductView: Received rating_value: {rating_value}")

        try:
            rating_value = int(rating_value)
            if not (1 <= rating_value <= 5):
                return JsonResponse({'error': 'Invalid rating value'}, status=400)
        except (ValueError, TypeError):
            print("RateProductView: Invalid rating_value or data")
            return JsonResponse({'error': 'Invalid JSON or data'}, status=400)

        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        if not hasattr(user, 'customer'):
            return JsonResponse({'error': 'Only customers can rate products'}, status=403)

        product = get_object_or_404(Product, pk=product_id)
        print(f"RateProductView: Found product: {product}")

        has_paid_order = Order.objects.filter(
            customer=user.customer,
            state=Order.STATE.PAID,
            order_items__product=product
        ).exists()
        print(f"RateProductView: Has paid order: {has_paid_order}")

        if not has_paid_order:
            return JsonResponse({'error': 'You cannot rate this product'}, status=403)

        rating = ProductRating.objects.create(
            user=user,
            product=product,
            rating=rating_value
        )
        return JsonResponse({'success': True})
