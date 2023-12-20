from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Area, Chore, HistoryItem, Option, CustomUser, AreaGroup, Month

class CustomUserAdmin(UserAdmin):
    # Customize the admin panel for your custom user model
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('password',)}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'profile_picture', 'male', 'user_color')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
    }),
)
    ordering = ('email',)
# Register your models here.

admin.site.register(Area)
admin.site.register(AreaGroup)
admin.site.register(Chore)
admin.site.register(HistoryItem)
admin.site.register(Option)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Month)
