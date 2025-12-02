from django import forms
from recipes.models.recipes import Recipe  # Changed from recepies
from recipes.models.recipes import Tag


class RecipeForm(forms.ModelForm):
    """
    Form for creating and updating recipes.
    """
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        """Form options."""

        model = Recipe
        fields = ['title', 'description', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter recipe title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your recipe...',
                'rows': 6
            }),

            'tags': forms.CheckboxSelectMultiple()
        }
        labels = {
            'title': 'Recipe Title',
            'description': 'Description',
        }

    def clean_title(self):
        """Validate and clean the recipe title."""
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise forms.ValidationError('Title cannot be empty.')
        if len(title.strip()) < 3:
            raise forms.ValidationError(
                'Title must be at least 3 characters long.')
        return title.strip()

    def clean_description(self):
        """Validate and clean the recipe description."""
        description = self.cleaned_data.get('description')
        if not description or not description.strip():
            raise forms.ValidationError('Description cannot be empty.')
        if len(description.strip()) < 10:
            raise forms.ValidationError(
                'Description must be at least 10 characters long.')
        return description.strip()
