from .models import ProductImage, Comment, Product, Discount, ProductRating
from django import forms


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'multiple': True}),
        }


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


class ProductRatingForm(forms.ModelForm):
    class Meta:
        model = ProductRating
        fields = ['rating', 'product']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].required = True
