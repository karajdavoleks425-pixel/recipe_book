from django.urls import path
from . import views

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('top/', views.top_recipes, name='top_recipes'),
    path('create/', views.recipe_create, name='recipe_create'),
    path('<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('<int:pk>/edit/', views.recipe_update, name='recipe_update'),
    path('<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
]