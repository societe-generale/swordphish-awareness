from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from LocalUsers.models import Region, RegionMembership, Entity, SwordphishUser

# Register your models here.


class SwordphishUserAdmin(admin.StackedInline):
    model = SwordphishUser


class MyUserAdmin(UserAdmin):
    inlines = (SwordphishUserAdmin, )
    list_display = ('username', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.register(Region)
admin.site.register(RegionMembership)
admin.site.register(Entity)
