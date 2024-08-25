from django.urls import path, re_path, include
from .views import (ProductListView, ProductDetailView, CommentSubmissionView, SubCategoryListView,
                    CategoryListView, ProductCreateView, ProductUpdateView, ProductSummaryListView,
                    ProductDeleteView, CustomerCommentsListView, CustomerDeleteView, RateProductView, CheckPurchaseView)

app_name = 'website'

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('product/add/', ProductCreateView.as_view(), name='product-add'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product-update'),
    path('product/summary', ProductSummaryListView.as_view(), name='product-summary'),
    path('product/<int:pk>/delete', ProductDeleteView.as_view(), name='product-delete'),

    re_path(r'^product/(?P<slug>[\w\u0600-\u06FF-]+)/$', ProductDetailView.as_view(), name='product-detail'),
    re_path(r'^product/(?P<slug>[\w\u0600-\u06FF-]+)/submit_comment/$', CommentSubmissionView.as_view(),
            name='submit_comment'),
    # Comments

    path('comments/list/', CustomerCommentsListView.as_view(), name='comment-list'),
    path('comments/delete/<int:pk>', CustomerDeleteView.as_view(), name='comment-delete'),

    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:category_id>/subcategories/', SubCategoryListView.as_view(), name='subcategory-list'),

    path('check-purchase/', CheckPurchaseView.as_view(), name='check_purchase'),
    path('rate-product/', RateProductView.as_view(), name='rate_product'),
]
