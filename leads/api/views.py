import jwt

from django.conf import settings

from rest_framework import response, status, views
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.viewsets import ModelViewSet

from utils.permissions import IsAuthenticated, IsAccountAdmin
from utils.helper_functions import send_or_verify_otp
from .serializers import (MemberSerializer,
                          AccountwithMemberSerializer,
                          RegisterSerializer,
                          UserSerializer,
                          )
from leads.models_user import Account, Member, User


class RegisterAPiView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(views.APIView):

    def post(self, request):
        data = request.data
        email = data.get('email', '')
        password = data.get('password', '')
        user = User.objects.filter(email=email).first()
        if not user:
            return response.Response({'error': 'User does not exist'}, status=status.HTTP_401_UNAUTHORIZED)

        authenticated = user.check_password(password)
        if not authenticated:
            return response.Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        resp_data, resp_status = send_or_verify_otp(user)
        return response.Response(resp_data, status=resp_status)


class LoginApiByTokenView(GenericAPIView):

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
        return response.Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class PrepareAccountView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AccountwithMemberSerializer

    def post(self, request):
        data = request.data
        account_serializer = self.serializer_class(data=data)
        if account_serializer.is_valid():
            account_serializer.save()

        account_id = account_serializer.data.get('id')
        member = Member()
        member.user = request.user
        member.account_id = account_id
        member.role = Member.USER_ROLE.admin
        member.status = Member.JOINED_STATUS.joined
        member.save()

        return response.Response(account_serializer.data, status=status.HTTP_201_CREATED)


class VerifyOTPView(GenericAPIView):

    def post(self, request):
        data = request.data
        email = data.get('email', '')
        if not email:
            return response.Response({'error': 'Email cannot be blank.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return response.Response({'error': 'User does not exist'}, status=status.HTTP_401_UNAUTHORIZED)

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
    permission_classes = (IsAccountAdmin,)
