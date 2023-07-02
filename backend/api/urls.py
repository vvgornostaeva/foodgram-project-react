from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AllSubscriptionViewSet,
                    IngredientViewSet,
                    RecipeViewSet,
                    SubscriptionView,
                    TagViewSet,
                    UserView)

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'users', UserView, basename='users')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/subscriptions/', AllSubscriptionViewSet.as_view(
        {'get': 'list'}),
        name='subscriptions'),
    path('users/<user_id>/subscribe/', SubscriptionView.as_view(),
         name='subscribe'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
