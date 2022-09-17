import jwt

from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from leads.api.serializers import UserSerializer
from leads.models_user import UserOTP

from rest_framework import status


def send_or_verify_otp(user, otp=None):
    user_otp = UserOTP.objects.filter(user=user).first()
    if not user_otp:
        random_str = get_random_string(6)
        userotp = UserOTP()
        userotp.user = user
        userotp.otp = random_str
        userotp.save()
        send_otp(user, user_otp)
        resp_data = {'error': 'Resending OTP. Check your email.'}
        resp_status = status.HTTP_400_BAD_REQUEST
        return resp_data, resp_status

    auth_token = jwt.encode({'email': user.email}, settings.SECRET_KEY, algorithm='HS256')
    if user_otp.is_verified:
        if not user.is_active:
            user.is_active = True
            user.save()
        user_serializer_data = UserSerializer(user).data
        resp_data = {'user': user_serializer_data, 'token': auth_token}
        resp_status = status.HTTP_200_OK
        return resp_data, resp_status

    if (not otp) and (not user_otp.is_verified):
        send_otp(user, user_otp)
        resp_data = {'error': f'Please verify your email {user.email}, OTP has been sent.'}
        resp_status = status.HTTP_400_BAD_REQUEST
        return resp_data, resp_status

    if user_otp.otp == otp:
        user_otp.is_verified = True
        user_otp.save()

        user.is_active = True
        user.save()

        user_serializer_data = UserSerializer(user).data
        resp_data = {'user': user_serializer_data, 'token': auth_token}
        resp_status = status.HTTP_200_OK
        return resp_data, resp_status
    else:
        user_otp.otp = get_random_string(6)
        user_otp.save()
        send_otp(user, user_otp)
        resp_data = {'error': 'Invalid OTP. Resending OTP. Check email.'}
        resp_status = status.HTTP_400_BAD_REQUEST
        return resp_data, resp_status


def send_otp(user, user_otp):
    subject = "Verify your email address.."
    message = f"{user_otp.otp} is your OTP."
    send_mail(subject=subject,
              message=message,
              from_email=settings.EMAIL_HOST_USER,
              recipient_list=[user.email],
              fail_silently=False)
