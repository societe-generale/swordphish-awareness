from django.urls import re_path, path

from Main.views import campaigns, templates, targets, users, actions, index, domains_feed

app_name = 'Main'

urlpatterns = [
    path('', index, name="index"),

    path('targets', targets.get_targets, name="get_targets"),
    path('targets/createlist', targets.create_targets_list, name="create_targets_list"),
    path('targets/deletelist/<int:listid>', targets.delete_targets_list, name="delete_targets_list"),
    path('targets/editlist/<int:listid>', targets.edit_targets_list, name="edit_targets_list"),
    path('targets/importtargerts/<int:listid>', targets.import_targets_list, name="import_targets_list"),
    path('targets/exporttargerts/<int:listid>', targets.export_targets_list, name="export_targets_list"),
    path('targets/createtarget/<int:listid>', targets.create_target, name="create_target"),
    path('targets/removetarget/<int:listid>/<int:targetid>', targets.delete_target, name="delete_target"),
    path('targets/edittarget/<int:listid>/<int:targetid>', targets.edit_target, name="edit_target"),
    path('targets/listtargets/<int:listid>', targets.list_targets, name="list_targets"),
    path('targets/listtargets/<int:listid>/<int:page>', targets.list_targets, name="list_targets"),
    path('targets/lists', targets.list_targets_list, name="list_targets_list"),
    path('targets/lists/<int:page>', targets.list_targets_list, name="list_targets_list_page"),

    path('templates', templates.get_templates, name="get_templates"),
    path('templates/create/<typeid>', templates.create_template, name="create_template"),
    path('templates/create/<typeid>/<int:duplicateid>', templates.create_template, name="create_template"),
    path('templates/edit/<int:templateid>', templates.edit_template, name="edit_template"),
    path('templates/delete/<int:templateid>', templates.delete_template, name="delete_template"),
    path('templates/view/<int:templateid>', templates.view_template, name="view_template"),
    path('templates/list', templates.list_template, name="list_template"),
    path('templates/list/<int:page>', templates.list_template, name="list_template"),

    path('campaigns', campaigns.get_campaigns, name="get_campaigns"),
    path('campaigns/running', campaigns.running_campaigns, name="running_campaigns"),
    path('campaigns/create/<typeid>', campaigns.create_campaign, name="create_campaign"),
    path('campaigns/create/<typeid>/<int:duplicateid>', campaigns.create_campaign, name="create_campaign"),
    path('campaigns/edit/<int:campaignid>', campaigns.edit_campaign, name="edit_campaign"),
    path('campaigns/delete/<int:campaignid>', campaigns.delete_campaign, name="delete_campaign"),
    path('campaigns/test/<int:campaignid>', campaigns.test_campaign, name="test_campaign"),
    path('campaigns/download/<int:campaignid>', campaigns.download_results, name="download_results"),
    path('campaigns/dasbhoard/<int:campaignid>', campaigns.display_dashboard, name="display_dashboard"),
    path('campaigns/reportids/<int:campaignid>', campaigns.submit_reported_ids, name="submit_reported_ids"),
    path('campaigns/list', campaigns.list_campaigns, name="list_campaigns"),
    path('campaigns/list/<int:page>', campaigns.list_campaigns, name="list_campaigns"),

    path('manage/entities', users.entities, name="admin_entities"),
    path('manage/regions', users.regions, name="admin_regions"),
    path('manage/users', users.users, name="admin_users"),

    re_path(r'^result/click/(?P<targetid>[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12})',
         actions.target_click,
         name="target_click"),
    re_path(r'^result/autoclick/(?P<targetid>[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12})',
         actions.target_autoclick,
         name="target_autoclick"),
    re_path(
        r'^result/displayawareness/(?P<targetid>[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12})',
        actions.display_awareness,
        name="display_awareness"),
    re_path(r'^result/getimage/(?P<templateid>\d+)/(?P<imgid>img\d+)$',
            actions.internet_explorer_img_hack,
            name="getimage"),
    re_path(r'^result/img/(?P<targetid>[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12})$',
            actions.target_openmail,
            name="target_openmail"),
    re_path(r'^result/report/(?P<targetid>[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12})$',
            actions.target_reportmail,
            name="target_reportmail"),
    re_path(r'^result/attach/(?P<targetid>[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12})$',
            actions.target_openattachment,
            name="target_openattachment"),

    path('2985836c7501af76a0bdd92f1d120cd2/domains_feed', domains_feed, name="domains_feed"),
]
