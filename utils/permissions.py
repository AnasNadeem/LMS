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


class IsAccountAdmin(BasePermission):

    def has_permission(self, request, view):
        member = Member.objects.filter(user=request.user).first()
        if not member:
            return False
        return bool(
            request.user and
            (request.user.is_authenticated and request.user.is_active) and
            (member.role == Member.USER_ROLE.admin))


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
