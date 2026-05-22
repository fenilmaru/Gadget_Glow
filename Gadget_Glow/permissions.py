from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_staff


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            hasattr(request.user, 'profile') and
            request.user.profile.role == 'seller'
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsProductOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'product') and hasattr(obj.product, 'seller'):
            return obj.product.seller == request.user
        return False


ROLE_PERMISSIONS = {
    'admin': ['add', 'change', 'delete', 'view'],
    'seller': ['add', 'change', 'view'],
    'customer': ['view'],
}


def has_role_permission(user, action):
    if user.is_staff or user.is_superuser:
        return True
    role = getattr(getattr(user, 'profile', None), 'role', 'customer')
    allowed = ROLE_PERMISSIONS.get(role, ['view'])
    return action in allowed
