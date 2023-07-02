from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsSuperUserAdminAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             ShoppingCartSerialiser,
                             SubscriptionCreateSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserCreateSerializer)
from api.utils import create_shopping_cart, delete_instance, post_instance
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart,
                            Subscription, Tag)
from users.models import User


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обьектов класса Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обьектов класса Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]


class UserView(UserViewSet):
    """Вьюсет для обьектов класса User."""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class SubscriptionView(APIView):
    """Вьюсет для удаления и изменениия подписок."""
    permission_classes = [IsSuperUserAdminAuthorOrReadOnly]

    def post(self, request, user_id):
        """Метод создания подписки."""
        author = get_object_or_404(User, id=user_id)
        data = {'user': request.user.id, 'author': author.id}
        serializer = SubscriptionCreateSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        """Метод удаления подписки."""
        author = get_object_or_404(User, id=user_id)
        user = get_object_or_404(User, id=request.user.id)
        if user.is_anonymous:
            return Response(
                {'detail': 'Учетные данные не были предоставлены'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        elif not Subscription.objects.filter(user=request.user,
                                             author=author
                                             ).exists():
            return Response(
                {'errors': 'Вы не подписаны на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.get(user=request.user,
                                 author=author).delete()
        return Response('Отписка прошла успешно',
                        status=status.HTTP_204_NO_CONTENT)


class AllSubscriptionViewSet(mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    """Вьюсет всех получения подписок."""
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = [IsSuperUserAdminAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """Метод добавления автора при создании рецепта."""
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Метод определения сериализатора."""
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """Метод отправления txt файла со списком покупок."""
        return create_shopping_cart(request)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        """Метод добавления и удаления из избранного."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return post_instance(request, recipe, FavoriteSerializer)
        error_message = ('Ошибка удаления из избранного. '
                         'Рецепта нет в избранном')
        success_message = 'Рецепт успешно удален из избранного'
        return delete_instance(request, Favorite, recipe, error_message,
                               success_message)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Метод добавления и удаления из списка покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return post_instance(request, recipe, ShoppingCartSerialiser)
        error_message = ('Ошибка удаления из списка покупок. '
                         'Рецепта нет в списке покупок')
        success_message = 'Рецепт успешно удален из списка покупок'
        return delete_instance(request, ShoppingCart, recipe,
                               error_message, success_message)
