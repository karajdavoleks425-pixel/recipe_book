from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Ingredient, Recipe, RecipeIngredient


class RecipeQueryCountTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='u1', password='x')
        self.cat = Category.objects.create(name='Супы')
        self.ing1 = Ingredient.objects.create(name='Картофель', unit='г')
        self.ing2 = Ingredient.objects.create(name='Морковь', unit='г')
        for i in range(5):
            r = Recipe.objects.create(
                title=f'Рецепт {i}', description='d',
                status='published', author=self.user, category=self.cat,
                base_servings=2,
            )
            RecipeIngredient.objects.create(recipe=r, ingredient=self.ing1, amount=100)
            RecipeIngredient.objects.create(recipe=r, ingredient=self.ing2, amount=50)

    def test_list_page_queries(self):
        # ТУТ БЫЛО 6, СТАЛО 5
        with self.assertNumQueries(5):
            self.client.get(reverse('recipe_list'))


class IngredientSearchTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='u2', password='x')
        self.cat = Category.objects.create(name='Салаты')
        self.ing1 = Ingredient.objects.create(name='Огурец', unit='г')
        self.ing2 = Ingredient.objects.create(name='Помидор', unit='г')
        self.r_both = Recipe.objects.create(
            title='Овощной', description='d', status='published',
            author=self.user, category=self.cat, base_servings=2,
        )
        RecipeIngredient.objects.create(recipe=self.r_both, ingredient=self.ing1, amount=100)
        RecipeIngredient.objects.create(recipe=self.r_both, ingredient=self.ing2, amount=100)
        self.r_one = Recipe.objects.create(
            title='Только огурец', description='d', status='published',
            author=self.user, category=self.cat, base_servings=2,
        )
        RecipeIngredient.objects.create(recipe=self.r_one, ingredient=self.ing1, amount=100)

    def test_all_selected_ingredients(self):
        # ТУТ ИСПРАВЛЕНА ПЕРЕДАЧА ПАРАМЕТРОВ
        url = f"{reverse('recipe_list')}?ingredients={self.ing1.id}&ingredients={self.ing2.id}"
        resp = self.client.get(url)
        self.assertContains(resp, 'Овощной')
        self.assertNotContains(resp, 'Только огурец')


class PortionRecalcTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='u3', password='x')
        self.cat = Category.objects.create(name='Каши')
        self.ing = Ingredient.objects.create(name='Крупа', unit='г')
        self.recipe = Recipe.objects.create(
            title='Каша', description='d', status='published',
            author=self.user, category=self.cat, base_servings=2,
        )
        RecipeIngredient.objects.create(recipe=self.recipe, ingredient=self.ing, amount=100)

    def test_scaling(self):
        resp = self.client.get(
            reverse('recipe_detail', args=[self.recipe.pk]),
            {'servings': 4},
        )
        self.assertContains(resp, '200')