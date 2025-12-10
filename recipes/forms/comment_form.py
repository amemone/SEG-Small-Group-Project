from django import forms
from recipes.models.comment import Comment

class CommentForm(forms.ModelForm):
    """
    Form for adding comments to recipes.
    """
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Write a comment...',
                'class': 'form-control',
                'rows': 3
            })
        }