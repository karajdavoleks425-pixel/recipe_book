from django import forms
from .models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'description', 'status', 'category',
                  'ingredients', 'base_servings')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'ingredients': forms.CheckboxSelectMultiple(),
        }