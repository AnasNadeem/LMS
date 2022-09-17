from django.urls import path
from .views import (
    RegisterAPiView,
    LoginApiView,
    LoginApiByTokenView,
    PrepareAccountView,
    VerifyOTPView,
)


urlpatterns = [
    # Authentication Urls
    path('register/', RegisterAPiView.as_view(), name='register'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('login_by_token/', LoginApiByTokenView.as_view(), name='login-by-token'),
    path('create_account/', PrepareAccountView.as_view(), name='create-account'),
    path('verify_otp/', VerifyOTPView.as_view(), name='verify-otp'),
]
