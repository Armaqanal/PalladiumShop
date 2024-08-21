from .models import ProductImage, Comment, Product, Discount
from django import forms


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'multiple': True}),
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['image'].required = False


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['created_at', 'updated_at', 'slug', 'company', 'rating_count', 'sum_rating', 'average_rating']
        widgets = {
            'description': forms.Textarea(),
        }


class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = '__all__'

# class ProductSummeryForm(forms.model):
#     class Meta:
#         model = Product
#         include=['name','category','price','discount']
