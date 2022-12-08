from django.contrib.sites.models import Site
from django.http import Http404

from utils.jwtauth import JWTAuthentication
from leads.models_user import Account, Member


class AccountMiddleware(object):
    domain = Site.objects.get_current().domain

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        request.account, request.member = None, None

        if not request.user.is_authenticated:
            JWTAuthentication().authenticate(request)

        if (not request.user) or (not request.user.is_authenticated):
            response = self.get_response(request)
            return response

        hostname = request.get_host()
        hostname_split_dot = hostname.split('.')
        domain_split_dot = self.domain.split('.')

        subdomain_split_dot = hostname_split_dot[:-len(domain_split_dot)]
        if subdomain_split_dot:
            subdomain = '.'.join(subdomain_split_dot)
            request.account = Account.objects.filter(subdomain__iexact=subdomain).first()
            request.member = request.user.member_set.all().first()
        else:
            request.member = Member.objects.filter(user=request.user).first() if request.user else None
            request.account = request.member.account if request.member else None

        if not request.account:
            response = self.get_response(request)
            return response

        if not getattr(request, 'member', None):
            raise Http404(f"Member {request.user.email} not found")

        response = self.get_response(request)
        return response
