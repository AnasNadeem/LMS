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
        account_id_list = request.user.member_set.all().value_list('account__pk')
        return obj.pk in account_id_list


class IsAccountMember(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        account_id_list = request.user.member_set.all().value_list('account__pk')
        return obj.account.pk in account_id_list


class IsAccountMemberAdmin(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        account_id_list = (request.user.member_set
                           .filter(role=Member.USER_ROLE.admin)
                           .value_list('account__pk')
                           )
        return obj.account.pk in account_id_list
