from django.urls import path
from .views import (
    RegisterAPiView,
    LoginApiView,
    LoginApiByTokenView,
    PrepareAccountView,
    VerifyOTPView,
    AccountView,
    AccountUserViewset,
)
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns


router = routers.SimpleRouter(trailing_slash=False)
router.register(r"accountuser", AccountUserViewset, basename="account_user")

urlpatterns = [
    # Authentication Urls
    path('register/', RegisterAPiView.as_view(), name='register'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('login_by_token/', LoginApiByTokenView.as_view(), name='login-by-token'),
    path('create_account/', PrepareAccountView.as_view(), name='create-account'),
    path('verify_otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('account/', AccountView.as_view(), name='fetch-account'),

]

urlpatterns += router.urls
urlpatterns = format_suffix_patterns(urlpatterns)
