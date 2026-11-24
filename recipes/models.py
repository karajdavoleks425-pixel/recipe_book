from django.conf import settings
from django.db import models


class Category(models.Model):
    """Справочник категорий."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиенты (связь многие-ко-многим с рецептами)."""
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=20, default='г')

    def __str__(self):
        return f'{self.name} ({self.unit})'


class Recipe(models.Model):
    """Основная модель — рецепт."""
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликован'),
    ]

    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
    )
    base_servings = models.PositiveIntegerField(default=2)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category', 'status']),
        ]

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    """Сколько ингредиента нужно на базовое число порций."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f'{self.recipe.title} — {self.ingredient.name}'