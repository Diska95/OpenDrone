from rest_framework.permissions import BasePermission


class IsDesigner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_role('designer')


class IsPrintNode(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_role('print_node')


class IsAssemblyCenter(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_role('assembly_center')


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.has_role('admin') or request.user.is_staff
        )


class IsCertifiedDesigner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.has_role('designer') and
            hasattr(request.user, 'designer_profile') and
            request.user.designer_profile.is_certified
        )
