from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Role, Permission, RolePermission, UserRole


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'middle_name', 'password', 'password_confirm')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    full_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'middle_name', 
                  'full_name', 'is_active', 'created_at', 'updated_at', 'roles')
        read_only_fields = ('id', 'email', 'is_active', 'created_at', 'updated_at')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_roles(self, obj):
        return [user_role.role.name for user_role in obj.user_roles.all()]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'middle_name')


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа в систему"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RoleSerializer(serializers.ModelSerializer):
    """Сериализатор для роли"""
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ('id', 'name', 'description', 'created_at', 'permissions')
        read_only_fields = ('id', 'created_at')
    
    def get_permissions(self, obj):
        return [f"{rp.permission.resource_type}:{rp.permission.action}" 
                for rp in obj.role_permissions.all()]


class PermissionSerializer(serializers.ModelSerializer):
    """Сериализатор для разрешения"""
    permission_string = serializers.SerializerMethodField()
    
    class Meta:
        model = Permission
        fields = ('id', 'resource_type', 'action', 'description', 'created_at', 'permission_string')
        read_only_fields = ('id', 'created_at')
    
    def get_permission_string(self, obj):
        return f"{obj.resource_type}:{obj.action}"


class RolePermissionSerializer(serializers.ModelSerializer):
    """Сериализатор для связи роли и разрешения"""
    permission_string = serializers.SerializerMethodField()
    
    class Meta:
        model = RolePermission
        fields = ('id', 'role', 'permission', 'permission_string', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def get_permission_string(self, obj):
        return f"{obj.permission.resource_type}:{obj.permission.action}"


class UserRoleSerializer(serializers.ModelSerializer):
    """Сериализатор для связи пользователя и роли"""
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ('id', 'user', 'role', 'role_name', 'assigned_at')
        read_only_fields = ('id', 'assigned_at')
