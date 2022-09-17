from django.contrib import admin
from leads.models_user import User, Account, AccountUser, UserOTP
from leads.models_lead import LeadAttribute, Lead, LeadUserMap
# Register your models here.


class TimeBaseModelAdmin(admin.ModelAdmin):
    list_display = ("created_at", "updated_at")


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "phone_number", "is_active")
    search_fields = ["email", "phone_number", "first_name", "last_name"]
    list_filter = ("is_active",)


class AccountAdmin(TimeBaseModelAdmin):
    list_display = ("name", "is_active",) + TimeBaseModelAdmin.list_display
    list_filter = ("is_active",)


class AccountUserAdmin(TimeBaseModelAdmin):
    list_display = ("user", "account", "role", "status",) + TimeBaseModelAdmin.list_display
    list_filter = ("status", "role", "account")


class UserOTPAdmin(TimeBaseModelAdmin):
    list_display = ("user", "otp", "is_verified",) + TimeBaseModelAdmin.list_display
    list_filter = ("is_verified",)


class LeadAttributeAdmin(TimeBaseModelAdmin):
    list_display = ("name", "slug", "account", "lead_type",
                    "attribute_type", "seq_no",) + TimeBaseModelAdmin.list_display
    list_filter = ("lead_type", "attribute_type", "account")
    search_fields = ["name", "slug", "seq_no"]


class LeadAdmin(TimeBaseModelAdmin):
    list_display = ("id", "account",) + TimeBaseModelAdmin.list_display
    list_filter = ("account",)


class LeadUserMapAdmin(TimeBaseModelAdmin):
    list_display = ("id", "accountuser") + TimeBaseModelAdmin.list_display


admin.site.register(User, UserAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(AccountUser, AccountUserAdmin)
admin.site.register(UserOTP, UserOTPAdmin)
admin.site.register(LeadAttribute, LeadAttributeAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(LeadUserMap, LeadUserMapAdmin)
