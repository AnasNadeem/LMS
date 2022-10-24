from rest_framework.permissions import BasePermission

from leads.models_user import Member


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and
            (request.user.is_authenticated and request.user.is_active))


class IsPartiallyAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class UserPermission(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class AccountPermission(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        account_id_list = request.user.member_set.all().values_list('account__pk')
        return obj.pk in account_id_list


class IsAccountMember(IsAuthenticated):

    def has_permission(self, request, view):
        if not request.account:
            return False
        return (super().has_permission(request, view) and request.member)


class IsAccountMemberAdmin(IsAccountMember):

    def has_permission(self, request, view):
        if not request.account:
            return False
        return (super().has_permission(request, view) and
                request.member.role == Member.USER_ROLE.admin)


class LeadAttributePermission(IsAccountMemberAdmin):

    def has_object_permission(self, request, view, obj):
        super().has_object_permission(request, view, obj)
        return obj.account.pk == request.account.pk
