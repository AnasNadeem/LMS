import csv
import jwt

from django.conf import settings
from django.contrib.postgres.fields.jsonb import KeyTextTransform
# from django.db.models.query import Q
from django.http import HttpResponse

from rest_framework import response, status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from utils.permissions import (IsAuthenticated,
                               IsAccountMember,
                               IsAccountMemberAdmin,
                               AccountPermission,
                               UserPermission,
                               )
from utils.helper_functions import send_or_verify_otp
from .serializers import (AccountSerializer,
                          AccountwithMemberSerializer,
                          LoginSerializer,
                          LeadSerializer,
                          LeadAttributeSerializer,
                          MemberSerializer,
                          MemberWithUserSerializer,
                          OtpSerializer,
                          RegisterSerializer,
                          TokenSerializer,
                          UserSerializer,
                          UserEmailSerializer,
                          )
from leads.models_user import Account, Member, User
from leads.models_lead import Lead, LeadAttribute


class UserViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = ()

    def get_permissions(self):
        user_permission_map = {
            "update": UserPermission
        }
        if user_permission_map.get(self.action.lower()):
            self.permission_classes = [user_permission_map.get(self.action.lower())]
        return super().get_permissions()

    def get_serializer_class(self):
        user_serializer_map = {
            "register": RegisterSerializer,
            "login": LoginSerializer,
            "forget_password": UserEmailSerializer,
            "verify_otp": OtpSerializer,
            "token_login": TokenSerializer,
        }
        return user_serializer_map.get(self.action.lower(), UserSerializer)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.filter(email=serializer.data.get('email')).first()
        resp_data, resp_status = send_or_verify_otp(user)
        return response.Response(resp_data, status=resp_status)

    @action(detail=False, methods=['post'])
    def login(self, request):
        data = request.data
        email = data.get('email', '')
        password = data.get('password', '')
        user = User.objects.filter(email=email).first()
        if not user:
            return response.Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        authenticated = user.check_password(password)
        if not authenticated:
            return response.Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        resp_data, resp_status = send_or_verify_otp(user)
        return response.Response(resp_data, status=resp_status)

    @action(detail=False, methods=['post'])
    def forget_password(self, request):
        data = request.data
        email = data.get('email', '')
        user = User.objects.filter(email=email).first()
        if not user:
            return response.Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        resp_data, resp_status = send_or_verify_otp(user, resent=True)
        return response.Response(resp_data, status=resp_status)

    @action(detail=False, methods=['post'])
    def token_login(self, request):
        data = request.data
        token = data.get('token')
        if not token:
            return response.Response({"status": "Token's field not provided"}, status=status.HTTP_400_BAD_REQUEST)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        user = User.objects.filter(email=payload['email']).first()
        if user:
            user_serializer_data = UserSerializer(user).data
            return response.Response(user_serializer_data, status=status.HTTP_200_OK)
        return response.Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        data = request.data
        email = data.get('email', '')
        if not email:
            return response.Response({'error': 'Email cannot be blank.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return response.Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        otp = data.get('otp', '')
        if not otp:
            return response.Response({'error': 'OTP cannot be blank.'}, status=status.HTTP_400_BAD_REQUEST)

        resp_data, resp_status = send_or_verify_otp(user, otp)
        return response.Response(resp_data, status=resp_status)


class AccountViewset(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountwithMemberSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        account_permission_map = {
            "create": IsAuthenticated,
            "download_csv": IsAccountMemberAdmin,
            "list": IsAuthenticated,
            "retrieve": IsAuthenticated,
            "update": IsAccountMemberAdmin,
            "partial_update": IsAccountMemberAdmin,
        }
        self.permission_classes = [account_permission_map.get(self.action.lower(), AccountPermission)]
        return super().get_permissions()

    def get_serializer_class(self):
        member_serializer_map = {
            "create": AccountSerializer,
            "list": AccountwithMemberSerializer,
            "retrieve": AccountwithMemberSerializer,
            "post": AccountSerializer,
            "put": AccountSerializer
        }
        return member_serializer_map.get(self.action.lower(), AccountSerializer)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return []
        members = self.request.user.member_set.all()
        accounts = [member.account for member in members]
        return accounts

    def create(self, request, *args, **kwargs):
        data = request.data
        account_serializer = self.get_serializer_class()
        account_serializer = account_serializer(data=data)
        account_serializer.is_valid(raise_exception=True)
        account_serializer.save()

        account_id = account_serializer.data.get('id')
        member = Member()
        member.user = request.user
        member.account_id = account_id
        member.role = Member.USER_ROLE.admin
        member.save()

        account = Account.objects.get(pk=account_id)
        account_member_serializer = AccountwithMemberSerializer(account)
        return response.Response(account_member_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download_csv(self, request, pk=None):
        account = self.get_object()
        lead_attrs = (account.leadattribute_set
                      .filter(lead_type=LeadAttribute.LEAD_CHOICES.main)
                      .values_list('slug', flat=True)
                      )
        if not lead_attrs:
            resp_data = {'error': 'Lead Structure not defined.'}
            resp_status = status.HTTP_400_BAD_REQUEST
            return response.Response(resp_data, status=resp_status)

        csv_response = HttpResponse(content_type='text/csv')

        filename = f'{account.name}.csv'
        csv_response['Content-Disposition'] = f'attachment; filename={filename}'
        writer = csv.DictWriter(csv_response, fieldnames=lead_attrs)
        writer.writeheader()
        return csv_response


class MemberViewset(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = (IsAccountMemberAdmin,)

    def get_serializer_class(self):
        member_serializer_map = {
            "get": MemberWithUserSerializer,
            "list": MemberWithUserSerializer,
            "retrieve": MemberWithUserSerializer,
            "post": MemberSerializer,
            "put": MemberSerializer
        }
        return member_serializer_map.get(self.action.lower(), MemberSerializer)

    def create(self, request, *args, **kwargs):
        # TODO - Send mail
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class LeadViewset(ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = (IsAccountMember,)

    account_pk_param = openapi.Schema('account_id', description='Account Id', type=openapi.TYPE_STRING)
    filters_param = openapi.Schema('filters', description='Filters', type=openapi.TYPE_OBJECT)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'account_id': account_pk_param, 'filters': filters_param}
    ))
    @action(detail=False, methods=['put'])
    def lead_filter(self, request):
        data = request.data
        account_id = data.get('account_id')
        filters = data.get('filters', {})
        # {
        # "trackdata1":[<option1>, <option2>],
        # "trackdata2":[<option1>, <option2>],
        # }
        account = Account.objects.filter(pk=account_id).first()
        if not account:
            resp_data = {'error': 'Invalud account'}
            resp_status = status.HTTP_400_BAD_REQUEST
            return response.Response(resp_data, status=resp_status)

        leads = account.lead_set.all()

        # lead_attrs = (account.leadattribute_set.all()
        #               .filter(lead_type=LeadAttribute.LEAD_CHOICES.track)
        #               )
        # error_list = []
        # for filter_key, filter_data in filters.items():
        #     key_leadattr = lead_attrs.filter(slug=filter_key).first()
        #     if not key_leadattr:
        #         error = f"Invalid key {filter_key}"
        #         error_list.append(error)
        #     for data in filter_data:
        # TODO - Create a validate function for Lead Attribute

        leads = self.filter_leads(leads, filters)
        lead_serializer = LeadSerializer(leads, many=True).data
        return response.Response(lead_serializer, status=status.HTTP_200_OK)

    def filter_leads(leads, filters):
        for filter_key, filter_value in filters.items():
            annotate_dict = {filter_key: KeyTextTransform(f'track__{filter_key}', 'fields')}
            query_dict = {f"{filter_key}__icontains": filter_value}
            leads = (leads
                     .annotate(**annotate_dict)
                     .filter(**query_dict)
                     )
        return leads


class LeadAttributeViewset(ModelViewSet):
    queryset = LeadAttribute.objects.all()
    serializer_class = LeadAttributeSerializer
    permission_classes = (IsAccountMemberAdmin,)

    # def get_queryset(self):
    #     if not self.request.user.is_authenticated:
    #         return []
    #     members = self.request.user.member_set.all()
    #     accounts = [member.account for member in members]
    #     return accounts
