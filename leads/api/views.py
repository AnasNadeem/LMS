import csv
import jwt

from django.conf import settings
from django.contrib.postgres.fields.jsonb import KeyTextTransform
# from django.db.models.query import Q
from django.http import HttpResponse

from rest_framework import response, status, views
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from utils.permissions import (IsAuthenticated,
                               IsAccountMember,
                               IsAccountMemberAdmin
                               )
from utils.helper_functions import send_or_verify_otp
from .serializers import (MemberSerializer,
                          AccountwithMemberSerializer,
                          RegisterSerializer,
                          UserSerializer,
                          LeadSerializer,
                          LeadAttributeSerializer,
                          )
from leads.models_user import Account, Member, User
from leads.models_lead import Lead, LeadAttribute


class RegisterAPiView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.filter(email=serializer.data.get('email')).first()
        resp_data, resp_status = send_or_verify_otp(user)
        return response.Response(resp_data, status=resp_status)


class LoginApiView(views.APIView):

    email_param = openapi.Schema('email', description='Email', type=openapi.TYPE_STRING)
    pass_param = openapi.Schema('password', description='Password', type=openapi.TYPE_STRING)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'email': email_param, 'password': pass_param}
    ))
    def post(self, request):
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


class ForgetPassApiView(views.APIView):

    email_param = openapi.Schema('email', description='Email', type=openapi.TYPE_STRING)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'email': email_param}
    ))
    def post(self, request):
        data = request.data
        email = data.get('email', '')
        user = User.objects.filter(email=email).first()
        if not user:
            return response.Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        resp_data, resp_status = send_or_verify_otp(user, resent=True)
        return response.Response(resp_data, status=resp_status)


class LoginApiByTokenView(views.APIView):

    token_param = openapi.Schema('token', description='Token', type=openapi.TYPE_STRING)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'token': token_param}
    ))
    def post(self, request):
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


class PrepareAccountView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AccountwithMemberSerializer

    def post(self, request):
        data = request.data
        account_serializer = self.serializer_class(data=data)
        account_serializer.is_valid(raise_exception=True)
        account_serializer.save()

        account_id = account_serializer.data.get('id')
        member = Member()
        member.user = request.user
        member.account_id = account_id
        member.role = Member.USER_ROLE.admin
        member.save()

        return response.Response(account_serializer.data, status=status.HTTP_201_CREATED)


class VerifyOTPView(views.APIView):

    email_param = openapi.Schema('email', description='Email', type=openapi.TYPE_STRING)
    otp_param = openapi.Schema('otp', description='OTP', type=openapi.TYPE_STRING)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'email': email_param, 'otp': otp_param}
    ))
    def post(self, request):
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


class AccountView(ListAPIView):
    queryset = Account.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = AccountwithMemberSerializer


class MemberViewset(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = (IsAccountMemberAdmin,)

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


class LeadAttributeViewset(ModelViewSet):
    queryset = LeadAttribute.objects.all()
    serializer_class = LeadAttributeSerializer
    permission_classes = (IsAccountMemberAdmin,)


class DownloadCSVLeadStructure(views.APIView):
    permission_classes = (IsAccountMemberAdmin,)

    account_pk_param = openapi.Parameter('pk', in_=openapi.IN_QUERY, description='Account Pk', type=openapi.TYPE_STRING, required=True)

    @swagger_auto_schema(manual_parameters=[account_pk_param])
    def get(self, request):
        account_pk = self.kwargs.get('pk')
        if not account_pk:
            resp_data = {'error': 'Account pk cannot be blank.'}
            resp_status = status.HTTP_400_BAD_REQUEST
            return response.Response(resp_data, status=resp_status)

        account = Account.objects.filter(pk=account_pk).first()
        if not account:
            resp_data = {'error': 'Invalid Account.'}
            resp_status = status.HTTP_400_BAD_REQUEST
            return response.Response(resp_data, status=resp_status)

        lead_attrs = (account.leadattribute_set
                      .filter(lead_type=LeadAttribute.LEAD_CHOICES.main)
                      .value_list('slug', flat=True)
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


class LeadFilterAPI(views.APIView):
    permission_classes = (IsAccountMember,)

    account_pk_param = openapi.Schema('account_id', description='Account Id', type=openapi.TYPE_STRING)
    filters_param = openapi.Schema('filters', description='Filters', type=openapi.TYPE_OBJECT)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'account_id': account_pk_param, 'filters': filters_param}
    ))
    def put(self, request):
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
