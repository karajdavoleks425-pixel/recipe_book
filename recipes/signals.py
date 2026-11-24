from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Recipe


@receiver([post_save, post_delete], sender=Recipe)
def clear_recipe_cache(sender, **kwargs):
    cache.delete('top_recipes')