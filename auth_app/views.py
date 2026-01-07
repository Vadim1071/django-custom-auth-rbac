from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate

from .models import User, Role, Permission, RolePermission, UserRole, AccessToken
from .serializers import (
    UserRegistrationSerializer, UserSerializer, UserUpdateSerializer,
    LoginSerializer, RoleSerializer, PermissionSerializer,
    RolePermissionSerializer, UserRoleSerializer
)
from .permissions import HasPermission, check_permission


class AuthViewSet(viewsets.ViewSet):
    """ViewSet для аутентификации"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Регистрация нового пользователя"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Создаем токен для нового пользователя
            token = AccessToken.generate_token()
            expires_at = timezone.now() + timedelta(days=30)
            access_token = AccessToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )
            return Response({
                'message': 'Пользователь успешно зарегистрирован',
                'token': token,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Вход в систему"""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'Аккаунт деактивирован'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not user.check_password(password):
            return Response(
                {'error': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Создаем новый токен
        token = AccessToken.generate_token()
        expires_at = timezone.now() + timedelta(days=30)
        access_token = AccessToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        return Response({
            'message': 'Успешный вход в систему',
            'token': token,
            'user': UserSerializer(user).data
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Выход из системы"""
        # Удаляем все токены пользователя
        AccessToken.objects.filter(user=request.user).delete()
        return Response({'message': 'Успешный выход из системы'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Получение информации о текущем пользователе"""
        return Response(UserSerializer(request.user).data)
    
    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_me(self, request):
        """Обновление профиля текущего пользователя"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Профиль успешно обновлен',
                'user': UserSerializer(request.user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_me(self, request):
        """Мягкое удаление аккаунта"""
        user = request.user
        # Деактивируем пользователя
        user.is_active = False
        user.save()
        # Удаляем все токены
        AccessToken.objects.filter(user=user).delete()
        return Response({'message': 'Аккаунт успешно удален'})


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet для управления ролями (только для администратора)"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Проверяем, является ли пользователь администратором
        check_permission(self.request.user, 'role', 'read')
        return super().get_queryset()
    
    def create(self, request, *args, **kwargs):
        check_permission(request.user, 'role', 'write')
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        check_permission(request.user, 'role', 'write')
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        check_permission(request.user, 'role', 'delete')
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def add_permission(self, request, pk=None):
        """Добавление разрешения к роли"""
        check_permission(request.user, 'role', 'write')
        role = self.get_object()
        permission_id = request.data.get('permission_id')
        
        if not permission_id:
            return Response(
                {'error': 'permission_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            permission = Permission.objects.get(pk=permission_id)
        except Permission.DoesNotExist:
            return Response(
                {'error': 'Разрешение не найдено'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        role_permission, created = RolePermission.objects.get_or_create(
            role=role,
            permission=permission
        )
        
        if created:
            return Response({
                'message': 'Разрешение успешно добавлено к роли',
                'data': RolePermissionSerializer(role_permission).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Разрешение уже существует для этой роли'
            })
    
    @action(detail=True, methods=['delete'])
    def remove_permission(self, request, pk=None):
        """Удаление разрешения из роли"""
        check_permission(request.user, 'role', 'write')
        role = self.get_object()
        permission_id = request.data.get('permission_id')
        
        if not permission_id:
            return Response(
                {'error': 'permission_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            role_permission = RolePermission.objects.get(
                role=role,
                permission_id=permission_id
            )
            role_permission.delete()
            return Response({'message': 'Разрешение успешно удалено из роли'})
        except RolePermission.DoesNotExist:
            return Response(
                {'error': 'Разрешение не найдено для этой роли'},
                status=status.HTTP_404_NOT_FOUND
            )


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра разрешений (только для администратора)"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        check_permission(request.user, 'permission', 'read')
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        check_permission(request.user, 'permission', 'read')
        return super().retrieve(request, *args, **kwargs)


class UserRoleViewSet(viewsets.ModelViewSet):
    """ViewSet для управления ролями пользователей (только для администратора)"""
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        check_permission(self.request.user, 'user_role', 'read')
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return UserRole.objects.filter(user_id=user_id)
        return super().get_queryset()
    
    def create(self, request, *args, **kwargs):
        check_permission(request.user, 'user_role', 'write')
        return super().create(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        check_permission(request.user, 'user_role', 'delete')
        return super().destroy(request, *args, **kwargs)


# Mock-представления для демонстрации работы системы
class MockProjectViewSet(viewsets.ViewSet):
    """Mock-представление для проектов"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Получение списка проектов (требует project:read)"""
        check_permission(request.user, 'project', 'read')
        projects = [
            {'id': 1, 'name': 'Проект 1', 'description': 'Описание проекта 1'},
            {'id': 2, 'name': 'Проект 2', 'description': 'Описание проекта 2'},
            {'id': 3, 'name': 'Проект 3', 'description': 'Описание проекта 3'},
        ]
        return Response(projects)
    
    def create(self, request):
        """Создание проекта (требует project:write)"""
        check_permission(request.user, 'project', 'write')
        return Response({
            'message': 'Проект успешно создан',
            'data': request.data
        }, status=status.HTTP_201_CREATED)


class MockDocumentViewSet(viewsets.ViewSet):
    """Mock-представление для документов"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Получение списка документов (требует document:read)"""
        check_permission(request.user, 'document', 'read')
        documents = [
            {'id': 1, 'title': 'Документ 1', 'content': 'Содержимое документа 1'},
            {'id': 2, 'title': 'Документ 2', 'content': 'Содержимое документа 2'},
            {'id': 3, 'title': 'Документ 3', 'content': 'Содержимое документа 3'},
        ]
        return Response(documents)
    
    def create(self, request):
        """Создание документа (требует document:write)"""
        check_permission(request.user, 'document', 'write')
        return Response({
            'message': 'Документ успешно создан',
            'data': request.data
        }, status=status.HTTP_201_CREATED)
