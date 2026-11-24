from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import RecipeForm
from .models import Category, Ingredient, Recipe


def recipe_list(request):
    """Список с фильтрами, поиском и спецкритерием №1."""
    qs = (Recipe.objects
          .select_related('author', 'category')
          .prefetch_related('ingredients')
          .order_by('-created_at')) 
    

    # фильтр по категории (справочнику)
    category_id = request.GET.get('category')
    if category_id:
        qs = qs.filter(category_id=category_id)

    # фильтр по статусу
    status = request.GET.get('status')
    if status:
        qs = qs.filter(status=status)

    # поиск по названию
    q = request.GET.get('q')
    if q:
        qs = qs.filter(title__icontains=q)

    # спецкритерий №1: рецепты, где есть ВСЕ выбранные ингредиенты

    ingredient_ids = request.GET.getlist('ingredients')
    if ingredient_ids:
        for ing_id in ingredient_ids:
            qs = qs.filter(ingredients__id=ing_id)
        qs = qs.distinct()

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'recipes/list.html', {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'statuses': Recipe.STATUS_CHOICES,
        'ingredients': Ingredient.objects.all(),
        'selected_ingredients': ingredient_ids,
        'selected_category': category_id,
        'selected_status': status,
        'q': q or '',
    })


def recipe_detail(request, pk):
    """Страница рецепта + спецкритерий №2 (пересчёт порций)."""
    recipe = get_object_or_404(
        Recipe.objects.select_related('author', 'category')
                      .prefetch_related('recipeingredient_set__ingredient'),
        pk=pk,
    )
    base = recipe.base_servings or 1
    try:
        requested = int(request.GET.get('servings', base))
    except ValueError:
        requested = base
    if requested < 1:
        requested = 1
    factor = requested / base

    scaled = [
        {
            'name': ri.ingredient.name,
            'unit': ri.ingredient.unit,
            'amount': round(float(ri.amount) * factor, 2),
        }
        for ri in recipe.recipeingredient_set.all()
    ]

    return render(request, 'recipes/detail.html', {
        'recipe': recipe,
        'scaled_ingredients': scaled,
        'requested_servings': requested,
    })


@require_http_methods(['GET', 'POST'])
def recipe_create(request):
    form = RecipeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.save()
        form.save_m2m()
        return redirect('recipe_detail', pk=recipe.pk)
    return render(request, 'recipes/form.html', {'form': form, 'title': 'Создать рецепт'})


@require_http_methods(['GET', 'POST'])
def recipe_update(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    form = RecipeForm(request.POST or None, instance=recipe)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('recipe_detail', pk=recipe.pk)
    return render(request, 'recipes/form.html', {'form': form, 'title': 'Редактировать рецепт'})


@require_http_methods(['GET', 'POST'])
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        recipe.delete()
        return redirect('recipe_list')
    return render(request, 'recipes/confirm_delete.html', {'recipe': recipe})


def top_recipes(request):
    """Дорогое вычисление, закэшированное."""
    data = cache.get('top_recipes')
    if data is None:
        data = list(
            Recipe.objects.annotate(ing_count=Count('ingredients'))
                          .order_by('-ing_count')[:10]
        )
        cache.set('top_recipes', data, 300)
    return render(request, 'recipes/top.html', {'top_recipes': data})