from rest_framework.permissions import BasePermission

from leads.models_user import AccountUser


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and
            (request.user.is_authenticated and request.user.is_active))


class IsPartiallyAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAccountAdmin(BasePermission):

    def has_permission(self, request, view):
        account_user = AccountUser.objects.filter(user=request.user).first()
        if not account_user:
            return False
        return bool(
            request.user and
            (request.user.is_authenticated and request.user.is_active) and
            (account_user.role == AccountUser.USER_ROLE.admin))
