from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class HasPermission(permissions.BasePermission):
    """
    Кастомное разрешение для проверки доступа к ресурсу
    Использование: permission_classes = [HasPermission('resource_type', 'action')]
    """
    
    def __init__(self, resource_type, action):
        self.resource_type = resource_type
        self.action = action
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Администратор имеет доступ ко всему
        if request.user.has_role('admin'):
            return True
        
        # Проверяем разрешение
        return request.user.has_permission(self.resource_type, self.action)


def check_permission(user, resource_type, action):
    """
    Функция для проверки разрешения в представлениях
    Вызывает PermissionDenied (403), если доступа нет
    """
    if not user or not user.is_authenticated:
        from rest_framework.exceptions import AuthenticationFailed
        raise AuthenticationFailed('Требуется аутентификация')
    
    # Администратор имеет доступ ко всему
    if user.has_role('admin'):
        return True
    
    # Проверяем разрешение
    if not user.has_permission(resource_type, action):
        raise PermissionDenied(f'У вас нет доступа к {resource_type}:{action}')
    
    return True
