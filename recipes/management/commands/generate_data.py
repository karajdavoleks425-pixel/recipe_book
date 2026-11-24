import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from recipes.models import Category, Ingredient, Recipe, RecipeIngredient


class Command(BaseCommand):
    help = 'Генерирует тестовые данные'

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')
        User = get_user_model()

        # 20 пользователей
        for i in range(20):
            username = f'user{i}'
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password='pass12345')
        users = list(User.objects.all()[:20])

        # 50 категорий
        Category.objects.bulk_create(
            [Category(name=f'Категория {i}') for i in range(50)],
            ignore_conflicts=True,
        )
        categories = list(Category.objects.all())

        # 200 ингредиентов
        Ingredient.objects.bulk_create(
            [Ingredient(name=f'Ингредиент {i}', unit='г') for i in range(200)],
            ignore_conflicts=True,
        )
        ingredients = list(Ingredient.objects.all())

        # 100 000 рецептов
        batch = []
        created = 0
        for i in range(100_000):
            batch.append(Recipe(
                title=f'Рецепт {i}',
                description=fake.text(max_nb_chars=500),
                status=random.choice(['draft', 'published']),
                author=random.choice(users),
                category=random.choice(categories),
                base_servings=random.randint(1, 8),
            ))
            if len(batch) >= 5000:
                Recipe.objects.bulk_create(batch)
                created += len(batch)
                batch = []
                self.stdout.write(f'Создано: {created}')
        if batch:
            Recipe.objects.bulk_create(batch)

        # Связи M2M (по 2–5 ингредиентов на рецепт)
        recipe_ids = list(Recipe.objects.values_list('id', flat=True))
        through = []
        for rid in recipe_ids:
            for ing in random.sample(ingredients, k=random.randint(2, 5)):
                through.append(RecipeIngredient(
                    recipe_id=rid, ingredient=ing,
                    amount=random.randint(10, 500),
                ))
            if len(through) >= 10_000:
                RecipeIngredient.objects.bulk_create(through, batch_size=5000)
                through = []
        if through:
            RecipeIngredient.objects.bulk_create(through, batch_size=5000)

        self.stdout.write(self.style.SUCCESS('Готово.'))