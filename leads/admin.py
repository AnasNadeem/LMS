from django.contrib import admin
from leads.models import User, Account, LeadAttribute, Lead, LeadUserMap
# Register your models here.


class TimeBaseModelAdmin(admin.ModelAdmin):
    list_display = ("created_at", "updated_at")


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name",
                    "phone_number", "is_staff", "is_admin",
                    "is_active",)
    list_filter = ("is_active", "is_admin")
    search_fields = ["username", "email", "phone_number", "first_name", "last_name"]


class AccountAdmin(TimeBaseModelAdmin):
    list_display = ("name", "is_active",) + TimeBaseModelAdmin.list_display
    list_filter = ("is_active",)


class LeadAttributeAdmin(TimeBaseModelAdmin):
    list_display = ("name", "slug", "account", "lead_type",
                    "attribute_type", "seq_no",) + TimeBaseModelAdmin.list_display
    list_filter = ("lead_type", "attribute_type", "account")
    search_fields = ["name", "slug", "seq_no"]


class LeadAdmin(TimeBaseModelAdmin):
    list_display = ("id", "account",) + TimeBaseModelAdmin.list_display
    list_filter = ("account",)


class LeadUserMapAdmin(TimeBaseModelAdmin):
    list_display = ("id", "user",) + TimeBaseModelAdmin.list_display
    list_filter = ("user",)


admin.site.register(User, UserAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(LeadAttribute, LeadAttributeAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(LeadUserMap, LeadUserMapAdmin)
