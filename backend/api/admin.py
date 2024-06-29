from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Area,
    Chore,
    HistoryItem,
    Option,
    CustomUser,
    AreaGroup,
    Month,
)
from import_export.admin import ImportExportModelAdmin


class CustomUserAdmin(UserAdmin):
    # Customize the admin panel for your custom user model
    list_display = ("email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    fieldsets = (
        (None, {"fields": ("password",)}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "profile_picture",
                    "male",
                    "user_color",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    ordering = ("email",)


class HistoryItemAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["completed_date", "completed_by", "chore"]

    ordering = ["completed_date", "chore", "completed_by"]


class AreaAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = [
        "area_name",
        "area_icon",
        "group",
        "area_order",
        "dirtiness",
        "dueCount",
    ]

    ordering = ["group", "area_order", "area_name"]

    list_filter = ["group"]


class AreaGroupAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["group_name", "group_order", "group_color"]

    ordering = ["group_order", "group_name"]


class OptionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        # Only allow adding if no instances exist
        return not Option.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Disable delete permission
        return False

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # Redirect to the singleton instance change page
        singleton = Option.load()
        if singleton:
            return super(OptionAdmin, self).change_view(
                request, str(singleton.pk), form_url, extra_context
            )
        else:
            return super(OptionAdmin, self).change_view(
                request, object_id, form_url, extra_context
            )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ["vacation_mode"]  # Make 'status' field read-only
        else:
            return []  # No fields are read-only for new objects

    list_display = ["vacation_mode", "med_thresh", "high_thresh"]


class MonthAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["name"]

    ordering = ["id"]


class ChoreAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = [
        "chore_name",
        "area",
        "status",
        "nextDue",
        "lastCompleted",
        "assignee",
        "effort",
        "vacationPause",
        "dirtiness",
        "duedays",
    ]

    ordering = [
        "status",
        "nextDue",
        "lastCompleted",
        "effort",
        "chore_name",
        "id",
    ]

    list_filter = ["area"]


# Register your models here.

admin.site.register(Area, AreaAdmin)
admin.site.register(AreaGroup, AreaGroupAdmin)
admin.site.register(Chore, ChoreAdmin)
admin.site.register(HistoryItem, HistoryItemAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Month, MonthAdmin)
