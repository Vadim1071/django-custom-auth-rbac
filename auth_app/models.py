from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
import secrets


class UserManager(BaseUserManager):
    """Менеджер для модели пользователя"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен для создания пользователя')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    """Модель пользователя"""
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=150, blank=True, null=True, verbose_name='Отчество')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'

    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"

    def get_full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)

    def has_role(self, role_name):
        """Проверяет, имеет ли пользователь указанную роль"""
        return self.user_roles.filter(role__name=role_name).exists()

    def has_permission(self, resource_type, action):
        """Проверяет, имеет ли пользователь разрешение на действие с ресурсом"""
        return self.user_roles.filter(
            role__role_permissions__permission__resource_type=resource_type,
            role__role_permissions__permission__action=action
        ).exists()


class Role(models.Model):
    """Модель роли"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        db_table = 'roles'

    def __str__(self):
        return self.name


class Permission(models.Model):
    """Модель разрешения"""
    resource_type = models.CharField(max_length=100, verbose_name='Тип ресурса')
    action = models.CharField(max_length=50, verbose_name='Действие')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Разрешение'
        verbose_name_plural = 'Разрешения'
        db_table = 'permissions'
        unique_together = [['resource_type', 'action']]

    def __str__(self):
        return f"{self.resource_type}:{self.action}"


class RolePermission(models.Model):
    """Связь роли и разрешения"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions', verbose_name='Роль')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions', verbose_name='Разрешение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Разрешение роли'
        verbose_name_plural = 'Разрешения ролей'
        db_table = 'role_permissions'
        unique_together = [['role', 'permission']]

    def __str__(self):
        return f"{self.role.name} - {self.permission}"


class UserRole(models.Model):
    """Связь пользователя и роли"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles', verbose_name='Пользователь')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles', verbose_name='Роль')
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='Назначена')

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        db_table = 'user_roles'
        unique_together = [['user', 'role']]

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


class AccessToken(models.Model):
    """Модель токена доступа"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_tokens', verbose_name='Пользователь')
    token = models.CharField(max_length=64, unique=True, verbose_name='Токен')
    expires_at = models.DateTimeField(verbose_name='Истекает')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name='Последнее использование')

    class Meta:
        verbose_name = 'Токен доступа'
        verbose_name_plural = 'Токены доступа'
        db_table = 'access_tokens'

    def __str__(self):
        return f"{self.user.email} - {self.token[:10]}..."

    @classmethod
    def generate_token(cls):
        """Генерирует уникальный токен"""
        return secrets.token_urlsafe(48)

    def is_expired(self):
        """Проверяет, истек ли токен"""
        return timezone.now() > self.expires_at

    def update_last_used(self):
        """Обновляет время последнего использования"""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])
