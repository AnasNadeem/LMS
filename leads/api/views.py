import csv
import jwt
import pandas as pd

from django.conf import settings
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.core.validators import validate_email
from django.db import transaction
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
                               LeadAttributePermission,
                               LeadPermission,
                               LeadUserMapPermission,
                               MemberPermission,
                               )
from utils.helper_functions import send_or_verify_otp
from .serializers import (AccountSerializer,
                          AccountwithMemberSerializer,
                          LoginSerializer,
                          LeadSerializer,
                          LeadAttributeSerializer,
                          LeadUserMapSerializer,
                          MemberSerializer,
                          MemberWithUserSerializer,
                          OtpSerializer,
                          RegisterSerializer,
                          TokenSerializer,
                          UserSerializer,
                          UserEmailSerializer,
                          ChangePasswordSerializer,
                          )
from leads.models_user import Account, Member, User
from leads.models_lead import Lead, LeadAttribute, LeadUserMap


class UserViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = ()

    def get_permissions(self):
        user_permission_map = {
            "update": UserPermission,
            'list': IsAuthenticated,
        }
        if self.action in user_permission_map:
            self.permission_classes = [user_permission_map.get(self.action)]
        return super().get_permissions()

    def get_serializer_class(self):
        user_serializer_map = {
            "create": RegisterSerializer,
            "login": LoginSerializer,
            "forget_password": UserEmailSerializer,
            "verify_otp": OtpSerializer,
            "token_login": TokenSerializer,
            "password_change": ChangePasswordSerializer,
        }
        return user_serializer_map.get(self.action.lower(), UserSerializer)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.filter(email=serializer.data.get('email')).first()
        resp_data, resp_status = send_or_verify_otp(request, user)
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

        resp_data, resp_status = send_or_verify_otp(request, user)
        return response.Response(resp_data, status=resp_status)

    @action(detail=False, methods=['post'])
    def forget_password(self, request):
        data = request.data
        email = data.get('email', '')
        user = User.objects.filter(email=email).first()
        if not user:
            return response.Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        resp_data, resp_status = send_or_verify_otp(request, user, resent=True)
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

        resp_data, resp_status = send_or_verify_otp(request, user, otp)
        return response.Response(resp_data, status=resp_status)

    @action(detail=False, methods=['put'])
    def password_change(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response("password changed successfully ", status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountViewset(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountwithMemberSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        account_permission_map = {
            "create": IsAuthenticated,
            "download_structure_csv": IsAccountMemberAdmin,
            "upload_leads_via_csv": IsAccountMemberAdmin,
            "list": IsAuthenticated,
            "retrieve": IsAuthenticated,
            "update": IsAccountMemberAdmin,
            "partial_update": IsAccountMemberAdmin,
            "destroy": IsAccountMemberAdmin
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
        return Account.objects.filter(pk=self.request.account.pk) if self.request.account else []

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

    @action(detail=False, methods=['get'])
    def download_structure_csv(self, request):
        account = request.account
        lead_attrs = (account.leadattribute_set
                      .values_list('slug', flat=True)
                      )
        if not lead_attrs:
            resp_data = {'error': 'Lead Structure not defined.'}
            resp_status = status.HTTP_400_BAD_REQUEST
            return response.Response(resp_data, status=resp_status)

        csv_response = HttpResponse(content_type='text/csv')

        filename = f'{account.subdomain}.csv'
        csv_response['Content-Disposition'] = f'attachment; filename={filename}'
        writer = csv.DictWriter(csv_response, fieldnames=lead_attrs)
        writer.writeheader()
        return csv_response

    @action(detail=False, methods=['post'])
    def upload_leads_via_csv(self, request):
        account = request.account
        file = request.data.get('file')
        if not file:
            return response.Response({'error': 'File required'}, status=status.HTTP_400_BAD_REQUEST)

        df = pd.read_csv(file)
        error_list = []
        lead_attrs = account.leadattribute_set.all()
        lead_attrs_slug = lead_attrs.values('slug')

        for lead_column in df.columns:
            if lead_column not in lead_attrs_slug:
                error = f"{lead_column} is invalid lead attribute. Download csv for attributes."
                error_list.append(error)
        if error_list:
            return response.Response({'error': error_list}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            for index, row in df.iterrows():
                # all_data = {slug: row[slug] for slug in df.columns}
                lead_data = {}
                for slug in df.columns:
                    lead_attr = lead_attrs.filter(slug=slug).first()
                    lead_data[lead_attr.lead_type] = row[slug]

                lead = Lead()
                lead.account = account
                lead.data = lead_data
                lead.save()

        return response.Response({}, status=status.HTTP_201_CREATED)


class MemberViewset(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = (MemberPermission,)

    def get_permissions(self):
        member_permission_map = {
            "create": IsAccountMemberAdmin,
            "update": IsAccountMemberAdmin,
            "invite_member": IsAccountMemberAdmin
        }
        self.permission_classes = [member_permission_map.get(self.action.lower(), IsAccountMemberAdmin)]
        return super().get_permissions()

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

    @action(detail=False, methods=['post'])
    def invite_member(self, request):
        account = request.account
        data = request.data
        email = data.get('email', '')
        role = data.get('role', '')

        if not email:
            return response.Response({'error': 'File required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_email(email)
        except Exception as e:
            e.message = f"Invalid email '{email}'"
            return response.Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)

        if role and (role not in Member.USER_ROLE):
            return response.Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_user(email=email)
            member = Member()
            member.account = account
            member.user = user
            member.role = role if role else Member.USER_ROLE.staff
            member.save()
            return response.Response({}, status=status.HTTP_201_CREATED)

        all_member_emails = account.member_set.all().value_list('user__email', flat=True)
        if user.email in all_member_emails:
            return response.Response({'error': 'User is already in the account'}, status=status.HTTP_400_BAD_REQUEST)

        member = Member()
        member.account = account
        member.user = user
        member.role = role if role else Member.USER_ROLE.staff
        member.save()
        return response.Response({}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return self.request.account.member_set.all() if self.request.account else []


class LeadViewset(ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = (LeadPermission,)

    def get_permissions(self):
        lead_permission_map = {
            "create": IsAccountMemberAdmin,
            "destroy": IsAccountMemberAdmin
        }
        self.permission_classes = [lead_permission_map.get(self.action.lower(), IsAccountMember)]
        return super().get_permissions()

    account_pk_param = openapi.Schema('account_id', description='Account Id', type=openapi.TYPE_STRING)
    filters_param = openapi.Schema('filters', description='Filters', type=openapi.TYPE_OBJECT)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'account_id': account_pk_param, 'filters': filters_param}
    ))
    @action(detail=False, methods=['put'])
    def lead_filter(self, request):
        filter_data = request.data
        # {
        # "leadattribute_slug":[<op>, <value>],
        # "leadattribute_slug":[<op>, <value>],
        # }
        account = request.account
        leads = account.lead_set.all()

        lead_attributes = (account.leadattribute_set.all())
        # Validate filter's leadattribute and its value
        Lead.clean_leadattr_data(Lead, filter_data, lead_attributes)

        leads = self.filter_leads(leads, lead_attributes, filter_data)
        lead_serializer = LeadSerializer(leads, many=True).data
        return response.Response(lead_serializer, status=status.HTTP_200_OK)

    def filter_leads(self, leads, lead_attributes, filter_data):
        for filter_key, filter_value in filter_data.items():
            lead_type = lead_attributes.get(slug=filter_key).lead_type
            annotate_dict = {filter_key: KeyTextTransform(f'{filter_key}', f'data__{lead_type}')}
            op, filter_value = (filter_value[0], filter_value[1]) if isinstance(filter_value, list) else (None, filter_value)
            query_filter = f"{filter_key}__{op}" if op else f"{filter_key}__icontains"
            query_dict = {query_filter: filter_value}
            leads = (leads
                     .annotate(**annotate_dict)
                     .filter(**query_dict)
                     )
        return leads

    def get_queryset(self):
        return self.request.account.lead_set.all() if self.request.account else []


class LeadAttributeViewset(ModelViewSet):
    queryset = LeadAttribute.objects.all()
    serializer_class = LeadAttributeSerializer
    permission_classes = (LeadAttributePermission,)

    def get_queryset(self):
        return self.request.account.leadattribute_set.all() if self.request.account else []


class LeadUserMapViewset(ModelViewSet):
    queryset = LeadUserMap.objects.all()
    serializer_class = LeadUserMapSerializer
    permission_classes = (LeadUserMapPermission,)
