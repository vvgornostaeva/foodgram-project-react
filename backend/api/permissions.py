from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsSuperUserAdminAuthorOrReadOnly(BasePermission):
    """Разрешает анонимному пользователю только безопасные запросы.
    Доступ к запросам PATCH и DELETE предоставляется только
    суперпользователю Джанго, админу Джанго, аутентифицированным пользователям
    с ролью admin, а также автору объекта.
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.is_superuser
                or request.user.is_staff
                or obj.author == request.user)
