from django.conf.urls import url
from LocalUsers import views

app_name = 'Authent'

urlpatterns = [
    url(r'^login$',
        views.user_login,
        name="login"
        ),
    url(r'^logout$',
        views.user_logout,
        name="logout"
        ),
    url(r'^login/changepwd$',
        views.password_change_mandatory,
        name="loginchangepwd"
        ),
    url(r'^login/lost-password$',
        views.password_lost,
        name='password_lost'
        ),
    url(r'^user/myprofile$',
        views.myprofile,
        name="myprofile"
        ),
    url(r'^user/(?P<userid>\d+)/edit$',
        views.edit_user,
        name="edit_user"
        ),
    url(r'^user/(?P<userid>\d+)/blockunblock$',
        views.block_unblock_user,
        name="block_unblock_user"
        ),
    url(r'^user/new$',
        views.new_user,
        name="new_user"
        ),
    url(r'^users/list/?(/(?P<emailcontains>[^/]{0,})/)?$',
        views.list_users,
        name="list_users"
        ),
    url(r'^entity/new$',
        views.new_entity,
        name="new_entity"
        ),
    url(r'^entity/list$',
        views.list_entities,
        name="list_entities"
        ),
    url(r'^entity/(?P<entityid>\d+)/edit/?$',
        views.edit_entity,
        name="edit_entity"
        ),
    url(r'^entity/(?P<entityid>\d+)/listadmins/?$',
        views.list_entity_admins,
        name="list_entity_admins"
        ),
    url(r'^entity/(?P<entityid>\d+)/addadmin/?$',
        views.add_entity_admin,
        name="add_entity_admin"
        ),
    url(r'^entity/(?P<entityid>\d+)/removeadmin/(?P<adminid>\d+)/?$',
        views.remove_entity_admin,
        name="remove_entity_admin"
        ),
    url(r'^region/new$',
        views.new_region,
        name="new_region"
        ),
    url(r'^region/list$',
        views.list_regions,
        name="list_regions"
        ),
    url(r'^region/(?P<regionid>\d+)/edit/?$',
        views.edit_region, name="edit_region"
        ),
    url(r'^region/(?P<regionid>\d+)/listusers/?$',
        views.list_region_users, name="list_region_users"
        ),
    url(r'^region/(?P<regionid>\d+)/adduser/?$',
        views.add_region_user, name="add_region_user"
        ),
    url(r'^region/(?P<regionid>\d+)/removeuser/(?P<userid>\d+)/?$',
        views.remove_region_user,
        name="remove_region_user"
        ),
]
