from errno import ECONNREFUSED
from os.path import exists
from re import findall

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET

from Main.core.campaign import test
from Main.forms import StandardCampaignForm, AttachmentCampaignForm, FakeFormCampaignForm, FakeRansomCampaignForm
from Main.forms import TestCampaignForm, ReportForm
from Main.models import Campaign


@login_required
@require_GET
def get_campaigns(request):
    return render(request, "Main/Campaigns/campaigns.html", {"menuactive": "campaigns",
                                                             "types": Campaign.CAMPAIGN_TYPES})


@login_required
@require_GET
def running_campaigns(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    return render(request, "Main/Campaigns/running_campaigns.html",
                  {"types": Campaign.CAMPAIGN_TYPES})


@login_required
def create_campaign(request, typeid, duplicateid=None):
    values = {}

    if duplicateid is not None:
        duplicate = get_object_or_404(Campaign, id=duplicateid)
        values = {
            "campaign_type": duplicate.campaign_type,
            "mail_template": duplicate.mail_template,
            "from_name": duplicate.from_name,
            "from_domain": duplicate.from_domain,
            "display_name": duplicate.display_name,
            "attachment_template": duplicate.attachment_template,
            "fake_form": duplicate.fake_form,
            "fake_ransom": duplicate.fake_ransom,
            "onclick_action": duplicate.onclick_action,
            "host_subdomain": duplicate.host_subdomain,
            "host_domain": duplicate.host_domain,
            "enable_mail_tracker": duplicate.enable_mail_tracker,
            "enable_attachment_tracker": duplicate.enable_attachment_tracker}

    if request.method == "GET":

        if typeid == "1":
            campaignform = StandardCampaignForm(initial=values, user=request.user)
        elif typeid == "2":
            campaignform = AttachmentCampaignForm(initial=values, user=request.user)
        elif typeid == "3":
            campaignform = FakeFormCampaignForm(initial=values, user=request.user)
        elif typeid == "4":
            campaignform = FakeRansomCampaignForm(initial=values, user=request.user)
        else:
            return HttpResponseForbidden()

        return render(request, 'Main/Campaigns/createcampaign.html',
                      {'campaignform': campaignform,
                       "typeid": typeid}
                      )

    elif request.method == "POST":

        if typeid == "1":
            campaignform = StandardCampaignForm(request.user, request.POST)
        elif typeid == "2":
            campaignform = AttachmentCampaignForm(request.user, request.POST)
        elif typeid == "3":
            campaignform = FakeFormCampaignForm(request.user, request.POST)
        elif typeid == "4":
            campaignform = FakeRansomCampaignForm(request.user, request.POST)
        else:
            return HttpResponseForbidden()

        if not campaignform.is_valid():
            return render(request, 'Main/Campaigns/createcampaign.html',
                          {'campaignform': campaignform,
                           "typeid": typeid}
                          )

        existing = Campaign.objects.filter(name=campaignform.cleaned_data["name"],
                                           author=request.user.swordphishuser)

        if existing:
            return render(request, 'Main/Campaigns/createcampaign.html',
                          {'campaignform': campaignform,
                           "typeid": typeid,
                           'campaign_already_exists': True}
                          )

        newcampaign = campaignform.save(commit=False)
        newcampaign.author = request.user.swordphishuser
        newcampaign.save()
        campaignform.save_m2m()

        return HttpResponse("Ok")
    else:
        return HttpResponseForbidden()


@login_required
def test_campaign(request, campaignid):
    campaign = get_object_or_404(Campaign, id=campaignid)

    if campaign.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if request.method == "GET":
        campaignform = TestCampaignForm(instance=campaign)
        campaignform.fields["recipient"].initial = request.user.email

        return render(request, 'Main/Campaigns/testcampaign.html',
                      {'campaignform': campaignform,
                       'campaign': campaign}
                      )

    if request.method == "POST":

        campaignform = TestCampaignForm(request.POST, instance=campaign)
        if not campaignform.is_valid():
            return render(request, 'Main/Campaigns/testcampaign.html',
                          {'campaignform': campaignform,
                           'campaign': campaign}
                          )

        recipient = campaignform.cleaned_data["recipient"]

        try:
            test(campaign, recipient)
        except Exception as e:
            if hasattr(e, "errno"):
                if e.errno == ECONNREFUSED:
                    return render(request, 'Main/Campaigns/testcampaign.html',
                                  {'campaignform': campaignform,
                                   'campaign': campaign,
                                   'connect_error': True}
                                  )
            else:
                raise e
        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def edit_campaign(request, campaignid):
    campaign = get_object_or_404(Campaign, id=campaignid)
    typeid = campaign.campaign_type

    if campaign.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if campaign.status == "2":
        return HttpResponseForbidden()

    if request.method == "GET":
        if typeid == "1":
            campaignform = StandardCampaignForm(request.user, instance=campaign)
        elif typeid == "2":
            campaignform = AttachmentCampaignForm(request.user, instance=campaign)
        elif typeid == "3":
            campaignform = FakeFormCampaignForm(request.user, instance=campaign)
        elif typeid == "4":
            campaignform = FakeRansomCampaignForm(request.user, instance=campaign)
        else:
            return HttpResponseForbidden()

        return render(request, 'Main/Campaigns/editcampaign.html',
                      {'campaignform': campaignform,
                       "typeid": typeid,
                       'campaign': campaign}
                      )

    if request.method == "POST":
        if typeid == "1":
            campaignform = StandardCampaignForm(request.user, request.POST, instance=campaign)
        elif typeid == "2":
            campaignform = AttachmentCampaignForm(request.user, request.POST, instance=campaign)
        elif typeid == "3":
            campaignform = FakeFormCampaignForm(request.user, request.POST, instance=campaign)
        elif typeid == "4":
            campaignform = FakeRansomCampaignForm(request.user, request.POST, instance=campaign)
        else:
            return HttpResponseForbidden()

        if not campaignform.is_valid():
            return render(request, 'Main/Campaigns/editcampaign.html',
                          {'campaignform': campaignform,
                           "typeid": typeid,
                           'campaign': campaign}
                          )

        result = Campaign.objects.filter(Q(name=campaignform.cleaned_data["name"]) &
                                         Q(author=request.user.swordphishuser) &
                                         ~Q(id=campaign.id))

        if result:
            return render(request, 'Main/Campaigns/editcampaign.html',
                          {'campaignform': campaignform,
                           "typeid": typeid,
                           'campaign_already_exists': True}
                          )

        campaign = campaignform.save(commit=False)
        campaignform.save_m2m()
        campaign.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def delete_campaign(request, campaignid):
    campaign = get_object_or_404(Campaign, id=campaignid)

    if campaign.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if campaign.status == "2":
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'Main/Campaigns/deletecampaign.html',
                      {'campaign': campaign}
                      )

    if request.method == "POST":

        anons = campaign.anonymous_targets.all()
        for anon in anons:
            anon.delete()
        campaign.delete()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
@require_GET
def list_campaigns(request, page=1):
    visible_users = request.user.swordphishuser.visible_users()
    campaignlist = Campaign.objects.filter(author__in=visible_users)
    paginator = Paginator(campaignlist, 20)
    paginator.ELLIPSIS = ''

    try:
        campaigns = paginator.page(page)
    except PageNotAnInteger:
        campaigns = paginator.page(1)
    except EmptyPage:
        campaigns = paginator.page(paginator.num_pages)
    except Exception:
        campaigns = paginator.page(1)

    campaigns.pages = paginator.get_elided_page_range(page)

    return render(request, 'Main/Campaigns/listcampaigns.html',
                  {"campaignlist": campaigns,
                   "current_user": request.user.swordphishuser})


@login_required
@require_http_methods(['GET', 'POST'])
def download_results(request, campaignid):
    campaign = get_object_or_404(Campaign, id=campaignid)

    if campaign.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if campaign.status != "3":
        return HttpResponseForbidden()

    excelmime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    filename = f'results/{campaignid}.xlsx'
    if not exists(filename):
        campaign.generate_results_xlsx()
    with open(filename, 'rb') as f:
        data = f.read()
    response = HttpResponse(data, content_type=excelmime)
    response['Content-Disposition'] = 'attachment; filename="%s_results.xlsx"' % campaign.name
    return response


@login_required
@require_GET
def display_dashboard(request, campaignid):
    campaign = get_object_or_404(Campaign, id=campaignid)

    if campaign.author not in request.user.swordphishuser.visible_users() or campaign.status not in '23':
        return HttpResponseForbidden()

    return render(request, 'Main/Campaigns/dashboard.html', {"campaign": campaign})


@login_required
def submit_reported_ids(request, campaignid):
    campaign = get_object_or_404(Campaign, id=campaignid)

    if campaign.status != "2" and campaign.status != "3":
        return HttpResponseForbidden()

    if request.method == "GET":
        reportform = ReportForm(instance=campaign)
        return render(request, 'Main/Campaigns/submit_reported_ids.html',
                      {"campaign": campaign,
                       "reportform": reportform}
                      )
    if request.method == "POST":
        regex = r'[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}'
        reportform = ReportForm(request.POST, instance=campaign)
        if not reportform.is_valid():
            return render(request, 'Main/Campaigns/submit_reported_ids.html',
                          {"campaign": campaign,
                           "reportform": reportform}
                          )
        text = reportform.cleaned_data['ids']
        ids = findall(regex, text)
        for i in ids:
            targetl = campaign.anonymous_targets.filter(uniqueid=i)
            if targetl:
                targetl[0].reported = True
                targetl[0].save()
        return HttpResponse("Ok")

    return HttpResponseForbidden()
