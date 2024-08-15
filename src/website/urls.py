from django.urls import path, re_path, include
from .views import ProductListView, ProductDetailView, CommentSubmissionView

app_name = 'website'

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    re_path(r'^product/(?P<slug>[\w\u0600-\u06FF-]+)/$', ProductDetailView.as_view(), name='product-detail'),
    # re_path(r'^product/(?P<slug>[\w\u0600-\u06FF-]+)/submit_comment/$', CommentSubmissionView.as_view(),
    #         name='submit_comment'),
    path('product/<int:product_id>/submit_comment/', CommentSubmissionView.as_view(), name='submit_comment'),
]
