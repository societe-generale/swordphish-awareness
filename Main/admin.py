from django.contrib import admin
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone

from Main.models import Target, TargetList, Attribute, AnonymousTarget
from Main.models import Campaign, Template, PhishmailDomain


# Register your models here.
admin.site.register(Target)
admin.site.register(TargetList)
admin.site.register(Attribute)
admin.site.register(AnonymousTarget)
admin.site.register(Campaign)
admin.site.register(Template)
admin.site.register(PhishmailDomain)


class SessionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(SessionAdmin, self).get_queryset(request)
        return qs.filter(expire_date__gt=timezone.now())

    def user(self, obj):
        session_data = obj.get_decoded()
        uid = session_data.get('_auth_user_id')
        if uid:
            user = User.objects.get(id=uid)
            return user.email
        return "unknown user"

    list_display = ['session_key', 'user']


admin.site.register(Session, SessionAdmin)
