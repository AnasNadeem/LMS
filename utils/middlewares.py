from django.contrib.sites.models import Site
from django.db.models.query import Q
from django.http import Http404

from leads.models_user import Account, AccountUser


class SubdomainMiddleware(object):
    domain = Site.objects.get_current().domain

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        hostname = request.get_host()

        request.account, request.subdomain = self.get_account_from_hostname(hostname)
        request.domain = self.domain
        request.account_user = None

        if getattr(request, 'account', None) and (not (request.user.is_authenticated and request.user.is_active)):
            raise Http404(f"Invalid user {request.user.email}")

        if getattr(request, 'account', None) and request.user.is_authenticated:
            request.account_user = (AccountUser.objects
                                    .filter(account=request.account, user=request.user)
                                    .filter(Q(status='pending') | Q(status='joined'))
                                    .first()
                                    )
            if not getattr(request, 'account_user', None):
                raise Http404(f"Account user {request.user.email} not found")

        response = self.get_response(request)
        return response

    @classmethod
    def get_account_from_hostname(cls, hostname):
        hostname_split_dot = hostname.split('.')
        domain_split_dot = cls.domain.split('.')

        if hostname_split_dot[-len(domain_split_dot):] != domain_split_dot:
            raise Http404(f"Domain {hostname} not found")

        subdomain_split_dot = hostname_split_dot[:-len(domain_split_dot)]
        subdomain = '.'.join(subdomain_split_dot)

        account = Account.objects.filter(subdomain__iexact=subdomain).first()

        if not account:
            raise Http404(f"Account {subdomain} not found")

        if not account.is_active:
            raise Http404(f"Account {subdomain} has been disabled")

        return account, subdomain
