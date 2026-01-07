from rest_framework import authentication, exceptions
from .models import AccessToken, User
from django.utils import timezone


class TokenAuthentication(authentication.BaseAuthentication):
    """Кастомная аутентификация по токену"""
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        # Проверяем формат заголовка: "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        token = parts[1]
        
        try:
            access_token = AccessToken.objects.select_related('user').get(token=token)
        except AccessToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Неверный токен доступа')
        
        # Проверяем, не истек ли токен
        if access_token.is_expired():
            raise exceptions.AuthenticationFailed('Токен истек')
        
        # Проверяем, активен ли пользователь
        if not access_token.user.is_active:
            raise exceptions.AuthenticationFailed('Пользователь деактивирован')
        
        # Обновляем время последнего использования
        access_token.update_last_used()
        
        return (access_token.user, access_token)
