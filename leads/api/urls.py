from django.urls import path
from .views import (
    RegisterAPiView,
    LoginApiView,
    LoginApiByTokenView,
    ForgetPassApiView,
    PrepareAccountView,
    VerifyOTPView,
    AccountView,
    MemberViewset,
    LeadViewset,
    LeadAttributeViewset,
    DownloadCSVLeadStructure,
    LeadFilterAPI,
)
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns


router = routers.SimpleRouter(trailing_slash=False)
router.register(r"member", MemberViewset, basename="member")
router.register(r"lead", LeadViewset, basename="lead")
router.register(r"leadattribute", LeadAttributeViewset, basename="leadattribute")

urlpatterns = [
    # Authentication Urls
    path('register/', RegisterAPiView.as_view(), name='register'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('login_by_token/', LoginApiByTokenView.as_view(), name='login-by-token'),
    path('create_account/', PrepareAccountView.as_view(), name='create-account'),
    path('forget_password/', ForgetPassApiView.as_view(), name='forget-password'),
    path('verify_otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('account/', AccountView.as_view(), name='fetch-account'),
    path('download_csv_structure/', DownloadCSVLeadStructure.as_view(), name='lead-structure'),
    path('lead_filter/', LeadFilterAPI.as_view(), name='lead-filter'),
]

urlpatterns += router.urls
urlpatterns = format_suffix_patterns(urlpatterns)
