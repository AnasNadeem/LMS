from .views import (
    AccountViewset,
    MemberViewset,
    LeadViewset,
    LeadAttributeViewset,
    LeadUserMapViewset,
    UserViewset,
)
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns


router = routers.SimpleRouter(trailing_slash=False)
router.register(r"account", AccountViewset, basename="account")
router.register(r"member", MemberViewset, basename="member")
router.register(r"lead", LeadViewset, basename="lead")
router.register(r"leadattribute", LeadAttributeViewset, basename="leadattribute")
router.register(r"leadusermap", LeadUserMapViewset, basename="leadusermap")
router.register(r"user", UserViewset, basename="user")

urlpatterns = []

urlpatterns += router.urls
urlpatterns = format_suffix_patterns(urlpatterns)
