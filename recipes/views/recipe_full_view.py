from django.views.generic import DetailView
from recipes.forms.comment_form import CommentForm
from recipes.models.comment import Comment
from recipes.models.recipes import Recipe


class RecipeFullView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_full.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'recipe'

    def get_object(self):
        recipe = super().get_object()
        return recipe
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        recipe = self.get_object()

        context['comments'] = Comment.objects.filter(recipe=recipe).order_by('-created_at')
        context['form'] = CommentForm()

        if self.request.user.is_authenticated:
            context['unread_count'] = self.request.user.notifications.filter(is_read=False).count()
        else:
            context['unread_count'] = 0
            
        return context
    
