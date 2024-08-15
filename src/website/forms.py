from .models import ProductImage, Comment
from django import forms


class ProductImageForm(forms.ModelForm):
    images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = ProductImage
        fields = '__all__'


# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ['text']
# widgets = {
#     'text': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Write a review'}),
# }


class CommentForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['product'].disabled = True
    #     self.fields['user'].disabled = True

        # OR set readonly widget attribute.

    # self.fields['name'].widget.attrs['readonly'] = True
    # self.fields['email'].widget.attrs['readonly'] = True

    class Meta:
        model = Comment
        fields = ['text']
