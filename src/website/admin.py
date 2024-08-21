from django.contrib import admin
from .models import Product, ProductRating, Discount, Category, Comment, ProductImage
from .forms import ProductImageForm


# Category Admin Configuration
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcategories', 'slug')


admin.site.register(Category, CategoryAdmin)



class DiscountAdmin(admin.ModelAdmin):
    list_display = ('percent', 'amount', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')

    def save_model(self, request, obj, form, change):
        try:
            obj.clean()
            super().save_model(request, obj, form, change)
        except ValueError as e:
            form.add_error(None, str(e))


admin.site.register(Discount, DiscountAdmin)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1 #TODO


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'inventory', 'company', 'final_price', 'is_discount_active', 'description')
    readonly_fields = ('final_price', 'average_rating', 'slug', 'sum_rating', 'rating_count')
    list_filter = ('company', 'discount', 'average_rating')
    search_fields = ('name', 'company__name')
    inlines = [ProductImageInline]

    def final_price(self, obj):
        return obj.final_price

    final_price.short_description = "قیمت نهایی"

    def is_discount_active(self, obj):
        return obj.discount.is_active() if obj.discount else False

    is_discount_active.boolean = True
    is_discount_active.short_description = "تخفیف فعاله؟"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductRating)
admin.site.register(Comment)
