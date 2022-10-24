from django.contrib.sites.models import Site
from django.http import Http404

from utils.jwtauth import JWTAuthentication
from leads.models_user import Account, Member


class AccountMiddleware(object):
    domain = Site.objects.get_current().domain

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        hostname = request.get_host()

        request.account = self.get_account_from_hostname(hostname)
        if not request.account:
            response = self.get_response(request)
            return response

        request.member = None
        if getattr(request, 'account', None) and (not request.user.is_authenticated):
            JWTAuthentication().authenticate(request)

        if not request.user:
            raise Http404(f"Invalid user {request.user}. Please verify.")

        request.member = (Member.objects
                          .filter(account=request.account)
                          .filter(user=request.user)
                          .first()
                          )
        if not getattr(request, 'member', None):
            raise Http404(f"Member {request.user.email} not found")

        response = self.get_response(request)
        return response

    @classmethod
    def get_account_from_hostname(cls, hostname):
        hostname_split_dot = hostname.split('.')
        domain_split_dot = cls.domain.split('.')

        subdomain_split_dot = hostname_split_dot[:-len(domain_split_dot)]
        if not subdomain_split_dot:
            return None

        subdomain = '.'.join(subdomain_split_dot)
        account = Account.objects.filter(subdomain__iexact=subdomain).first()

        if not account:
            raise Http404(f"Account {subdomain} not found")

        if not account.is_active:
            raise Http404(f"Account {subdomain} has been disabled")

        return account
