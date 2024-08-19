from .models import ProductImage, Comment, Product, Discount
from django import forms


class ProductImageForm(forms.ModelForm):
    images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = ProductImage
        fields = ['image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['created_at', 'updated_at', 'slug', 'company','rating_count','sum_rating','average_rating']
        widgets = {
            'description': forms.Textarea(),
        }


class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = '__all__'
