from django.core.management.base import BaseCommand
from django.utils import timezone
from auth_app.models import User, Role, Permission, RolePermission, UserRole


class Command(BaseCommand):
    help = 'Инициализация тестовых данных для системы аутентификации и авторизации'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')
        
        # Создаем разрешения
        permissions_data = [
            ('project', 'read', 'Чтение проектов'),
            ('project', 'write', 'Создание и изменение проектов'),
            ('project', 'delete', 'Удаление проектов'),
            ('document', 'read', 'Чтение документов'),
            ('document', 'write', 'Создание и изменение документов'),
            ('document', 'delete', 'Удаление документов'),
            ('role', 'read', 'Просмотр ролей'),
            ('role', 'write', 'Создание и изменение ролей'),
            ('role', 'delete', 'Удаление ролей'),
            ('permission', 'read', 'Просмотр разрешений'),
            ('user_role', 'read', 'Просмотр ролей пользователей'),
            ('user_role', 'write', 'Назначение ролей пользователям'),
            ('user_role', 'delete', 'Удаление ролей у пользователей'),
        ]
        
        permissions = {}
        for resource_type, action, description in permissions_data:
            perm, created = Permission.objects.get_or_create(
                resource_type=resource_type,
                action=action,
                defaults={'description': description}
            )
            permissions[f'{resource_type}:{action}'] = perm
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создано разрешение: {resource_type}:{action}'))
        
        # Создаем роли
        roles_data = [
            ('admin', 'Администратор - полный доступ ко всем ресурсам'),
            ('manager', 'Менеджер - управление проектами и чтение документов'),
            ('user', 'Пользователь - только чтение проектов и документов'),
        ]
        
        roles = {}
        for role_name, description in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={'description': description}
            )
            roles[role_name] = role
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана роль: {role_name}'))
        
        # Назначаем разрешения ролям
        # Администратор - все разрешения
        admin_permissions = [
            'project:read', 'project:write', 'project:delete',
            'document:read', 'document:write', 'document:delete',
            'role:read', 'role:write', 'role:delete',
            'permission:read',
            'user_role:read', 'user_role:write', 'user_role:delete',
        ]
        
        for perm_key in admin_permissions:
            RolePermission.objects.get_or_create(
                role=roles['admin'],
                permission=permissions[perm_key]
            )
        
        # Менеджер - проекты (read, write) и документы (read)
        manager_permissions = [
            'project:read', 'project:write',
            'document:read',
        ]
        
        for perm_key in manager_permissions:
            RolePermission.objects.get_or_create(
                role=roles['manager'],
                permission=permissions[perm_key]
            )
        
        # Пользователь - только чтение
        user_permissions = [
            'project:read',
            'document:read',
        ]
        
        for perm_key in user_permissions:
            RolePermission.objects.get_or_create(
                role=roles['user'],
                permission=permissions[perm_key]
            )
        
        self.stdout.write(self.style.SUCCESS('Разрешения назначены ролям'))
        
        # Создаем тестовых пользователей
        users_data = [
            ('admin@example.com', 'admin123', 'Админ', 'Админов', 'Админович', 'admin'),
            ('manager@example.com', 'manager123', 'Менеджер', 'Менеджеров', 'Менеджерович', 'manager'),
            ('user@example.com', 'user123', 'Пользователь', 'Пользователев', 'Пользователевич', 'user'),
        ]
        
        for email, password, first_name, last_name, middle_name, role_name in users_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'middle_name': middle_name,
                }
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {email}'))
            
            # Назначаем роль
            UserRole.objects.get_or_create(
                user=user,
                role=roles[role_name]
            )
        
        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))
        self.stdout.write('\nТестовые пользователи:')
        self.stdout.write('  - admin@example.com / admin123 (администратор)')
        self.stdout.write('  - manager@example.com / manager123 (менеджер)')
        self.stdout.write('  - user@example.com / user123 (пользователь)')
