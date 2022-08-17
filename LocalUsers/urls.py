from django.urls import re_path
from LocalUsers import views

app_name = 'Authent'

urlpatterns = [
    re_path(r'^login$',
        views.user_login,
        name="login"
        ),
    re_path(r'^logout$',
        views.user_logout,
        name="logout"
        ),
    re_path(r'^login/changepwd$',
        views.password_change_mandatory,
        name="loginchangepwd"
        ),
    re_path(r'^login/lost-password$',
        views.password_lost,
        name='password_lost'
        ),
    re_path(r'^user/myprofile$',
        views.myprofile,
        name="myprofile"
        ),
    re_path(r'^user/(?P<userid>\d+)/edit$',
        views.edit_user,
        name="edit_user"
        ),
    re_path(r'^user/(?P<userid>\d+)/blockunblock$',
        views.block_unblock_user,
        name="block_unblock_user"
        ),
    re_path(r'^user/new$',
        views.new_user,
        name="new_user"
        ),
    re_path(r'^users/list/?(/(?P<emailcontains>[^/]{0,})/)?$',
        views.list_users,
        name="list_users"
        ),
    re_path(r'^entity/new$',
        views.new_entity,
        name="new_entity"
        ),
    re_path(r'^entity/list$',
        views.list_entities,
        name="list_entities"
        ),
    re_path(r'^entity/(?P<entityid>\d+)/edit/?$',
        views.edit_entity,
        name="edit_entity"
        ),
    re_path(r'^entity/(?P<entityid>\d+)/listadmins/?$',
        views.list_entity_admins,
        name="list_entity_admins"
        ),
    re_path(r'^entity/(?P<entityid>\d+)/addadmin/?$',
        views.add_entity_admin,
        name="add_entity_admin"
        ),
    re_path(r'^entity/(?P<entityid>\d+)/removeadmin/(?P<adminid>\d+)/?$',
        views.remove_entity_admin,
        name="remove_entity_admin"
        ),
    re_path(r'^region/new$',
        views.new_region,
        name="new_region"
        ),
    re_path(r'^region/list$',
        views.list_regions,
        name="list_regions"
        ),
    re_path(r'^region/(?P<regionid>\d+)/edit/?$',
        views.edit_region, name="edit_region"
        ),
    re_path(r'^region/(?P<regionid>\d+)/listusers/?$',
        views.list_region_users, name="list_region_users"
        ),
    re_path(r'^region/(?P<regionid>\d+)/adduser/?$',
        views.add_region_user, name="add_region_user"
        ),
    re_path(r'^region/(?P<regionid>\d+)/removeuser/(?P<userid>\d+)/?$',
        views.remove_region_user,
        name="remove_region_user"
        ),
]
