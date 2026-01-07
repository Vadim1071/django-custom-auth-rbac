from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet, RoleViewSet, PermissionViewSet,
    UserRoleViewSet, MockProjectViewSet, MockDocumentViewSet
)

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')
router.register(r'projects', MockProjectViewSet, basename='project')
router.register(r'documents', MockDocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
]
