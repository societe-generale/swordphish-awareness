import errno
import re
import json
from base64 import b64decode
from datetime import datetime
from django.utils.timezone import get_current_timezone
from zipfile import BadZipfile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.forms.formsets import formset_factory
from django.db.models import Q
from django.conf import settings
from bs4 import BeautifulSoup
from LocalUsers.forms import SwordphishUserForm, UserForm
from Main.models import TargetList, Target, AnonymousTarget, Campaign, Template, PhishmailDomain
from Main.forms import TargetsListForm, NewTargetForm, AttributeForm, StandardCampaignForm
from Main.forms import AttachmentCampaignForm, SimpleMailForm, MailWithAttachmentForm
from Main.forms import AttachmentForm, Redirection, Awareness, CredsHarvesterForm
from Main.forms import TestCampaignForm, ReportForm, FakeRansomForm, FakeRansomCampaignForm
from Main.forms import FakeFormCampaignForm
from os.path import exists

def validate_domain(function):
    hosting_domain = settings.HOSTING_DOMAIN

    def _dec(func):
        def _view(request, *args, **kwargs):
            if "HTTP_HOST" not in request.META:
                return HttpResponseForbidden()

            values = [
                      re.compile(hosting_domain),
                      re.compile("localhost:?.*"),
                      re.compile("127.0.0.1:?.*")
                     ]

            if any(regex.match(request.META["HTTP_HOST"]) for regex in values):
                return func(request, *args, **kwargs)

            return HttpResponseForbidden()

        _view.__name__ = func.__name__
        _view.__dict__ = func.__dict__
        _view.__doc__ = func.__doc__

        return _view

    return _dec(function)


@validate_domain
@login_required
def index(request):
    # pylint: disable=W0613
    return redirect("Main:campaign_campaigns")


@validate_domain
@login_required
def campaign_overview(request):
    return render(request, "Main/Campaigns/overview.html", {"menuactive": "overview"})


@validate_domain
@login_required
def campaign_targets(request):
    return render(request, "Main/Campaigns/Targets/targets.html", {"menuactive": "targets"})


@validate_domain
@login_required
def campaign_create_targets_list(request):
    if request.method == "GET":
        targetlistform = TargetsListForm()
        return render(request, 'Main/Campaigns/Targets/newtargetslist.html',
                      {'targetlistform': targetlistform}
                      )

    if request.method == "POST":
        targetlistform = TargetsListForm(request.POST)

        if not targetlistform.is_valid():
            return render(request, 'Main/Campaigns/Targets/newtargetslist.html',
                          {'targetlistform': targetlistform}
                          )

        if TargetList.objects.filter(name=targetlistform.cleaned_data["name"],
                                     author=request.user.swordphishuser):
            return render(request, 'Main/Campaigns/Targets/newtargetslist.html',
                          {'targetlistform': targetlistform,
                          'list_already_exists': True}
                          )

        targetlist = targetlistform.save(commit=False)
        targetlist.author = request.user.swordphishuser
        targetlist.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_delete_targets_list(request, listid):
    targetlist = get_object_or_404(TargetList, id=listid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'Main/Campaigns/Targets/deletetargetslist.html',
                      {'targetlist': targetlist}
                      )

    if request.method == "POST":
        if targetlist.is_used():
            return render(request, 'Main/Campaigns/Targets/deletetargetslist.html',
                          {'targetlist': targetlist, 'targetlistused': True}
                          )
        targetlist.targets.all().delete()
        targetlist.delete()
        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_edit_targets_list(request, listid):
    targetlist = get_object_or_404(TargetList, id=listid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if request.method == "GET":
        targetlistform = TargetsListForm(instance=targetlist)
        return render(request, 'Main/Campaigns/Targets/edittargetslist.html',
                      {'targetlistform': targetlistform,
                      'listid': listid}
                      )

    if request.method == "POST":
        targetlistform = TargetsListForm(request.POST)

        if not targetlistform.is_valid():
            return render(request, 'Main/Campaigns/Targets/edittargetslist.html',
                          {'targetlistform': targetlistform,
                          'listid': listid}
                          )

        if TargetList.objects.filter(name=targetlistform.cleaned_data["name"],
                                     author=request.user.swordphishuser):
            return render(request, 'Main/Campaigns/Targets/edittargetslist.html',
                          {'targetlistform': targetlistform,
                          'list_already_exists': True,
                          'listid': listid}
                          )

        targetlist.name = targetlistform.cleaned_data["name"]
        targetlist.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_import_targets_list(request, listid):
    targetlist = get_object_or_404(TargetList, id=listid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'Main/Campaigns/Targets/importtargetslist.html',
                      {'targetlist': targetlist,
                      'listid': listid}
                      )

    if request.method == "POST":

        try:
            f = request.FILES['targetlist']
        except MultiValueDictKeyError:
            return render(request, 'Main/Campaigns/Targets/importtargetslist.html',
                          {'targetlist': targetlist,
                          'listid': listid,
                          'bad_format_file': True}
                          )

        try:
            targetlist.loadTargetsFromUploadedXslx(f)
        except BadZipfile:
            return render(request, 'Main/Campaigns/Targets/importtargetslist.html',
                          {'targetlist': targetlist,
                          'listid': listid,
                          'bad_file': True}
                          )
        except ValidationError as e:
            return render(request, 'Main/Campaigns/Targets/importtargetslist.html',
                          {'targetlist': targetlist,
                          'listid': listid,
                          'bademail': True,
                          'exception': e}
                          )
        except Exception:
            import logging
            logger = logging.getLogger('django.request')
            logger.exception(extra={'request': request})
            return render(request, 'Main/Campaigns/Targets/importtargetslist.html',
                          {'targetlist': targetlist,
                          'listid': listid,
                          'unknown_error': True}
                          )

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_export_targets_list(request, listid):
    targetlist = get_object_or_404(TargetList, id=listid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if request.method == "GET" or request.method == "POST":
        excelmime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(targetlist.export_to_xlsx(), content_type=excelmime)
        response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % targetlist.name
        return response

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_create_target(request, listid):
    targetlist = get_object_or_404(TargetList, id=listid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    targetform = NewTargetForm()
    attributeformset = formset_factory(AttributeForm, extra=0)

    if request.method == "GET":
        return render(request, 'Main/Campaigns/Targets/createtarget.html',
                      {'targetlist': targetlist,
                      'targetform': targetform,
                      'attributeformset': attributeformset,
                      'listid': listid}
                      )

    if request.method == "POST":
        targetform = NewTargetForm(request.POST)
        attributeformset = attributeformset(request.POST)

        if (not targetform.is_valid()) or (not attributeformset.is_valid()):
            return render(request, 'Main/Campaigns/Targets/createtarget.html',
                          {'targetlist': targetlist,
                          'targetform': targetform,
                          'attributeformset': attributeformset,
                          'listid': listid}
                          )

        existing = targetlist.targets.filter(mail_address=targetform.cleaned_data["mail_address"])

        if existing:
            return render(request, 'Main/Campaigns/Targets/createtarget.html',
                          {'targetlist': targetlist,
                          'targetform': targetform,
                          'attributeformset': attributeformset,
                          'listid': listid,
                          'target_already_exists': True}
                          )

        newtarget = targetform.save()

        for attform in attributeformset:
            if "key" in attform.cleaned_data.keys() and "value" in attform.cleaned_data.keys():
                newtarget.addAttribute(attform.cleaned_data["key"], attform.cleaned_data["value"])

        targetlist.targets.add(newtarget)

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_edit_target(request, listid, targetid):
    target = get_object_or_404(Target, id=targetid)
    targetlist = get_object_or_404(TargetList, id=listid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if not targetlist.targets.filter(id=targetid):
        return HttpResponseForbidden()

    targetform = NewTargetForm(instance=target)

    formset = formset_factory(AttributeForm, extra=0)

    attformset = formset(initial=target.attributes.all().values())

    if request.method == "GET":
        return render(request, 'Main/Campaigns/Targets/edittarget.html',
                      {'targetlist': targetlist,
                      'targetid': targetid,
                      'targetform': targetform,
                      'attformset': attformset}
                      )

    if request.method == "POST":
        targetform = NewTargetForm(request.POST)
        attformset = formset(request.POST)

        if not (targetform.is_valid() and attformset.is_valid()):
            return render(request, 'Main/Campaigns/Targets/edittarget.html',
                          {'targetlist': targetlist,
                          'targetid': targetid,
                          'targetform': targetform,
                          'attformset': attformset}
                          )

        tl = targetlist.targets.filter(mail_address=targetform.cleaned_data["mail_address"])

        for tar in tl:
            if tar.id != target.id:
                return render(request, 'Main/Campaigns/Targets/edittarget.html',
                              {'targetlist': targetlist,
                              'targetid': targetid,
                              'targetform': targetform,
                              'attformset': attformset,
                              'target_already_exists': True}
                              )

        target.mail_address = targetform.cleaned_data["mail_address"]
        target.save()
        target.attributes.all().delete()
        for attform in attformset:
            target.addAttribute(attform.cleaned_data["key"], attform.cleaned_data["value"])

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_list_targets(request, listid, page=1):
    targetlist = get_object_or_404(TargetList, id=listid)

    editable = True

    if targetlist.author not in request.user.swordphishuser.visible_users():
        editable = False

    paginator = Paginator(targetlist.targets.all().order_by("mail_address"), 10)
    paginator.ELLIPSIS = ''

    try:
        targets = paginator.page(page)
    except PageNotAnInteger:
        targets = paginator.page(1)
    except EmptyPage:
        targets = paginator.page(paginator.num_pages)
    except Exception:
        targets = paginator.page(1)

    targets.pages = paginator.get_elided_page_range(page)

    if request.method == "GET":
        return render(request, 'Main/Campaigns/Targets/listtargets.html',
                      {'targetlist': targetlist,
                      'targets': targets,
                      'listname': targetlist.name,
                      'listid': listid,
                      'editable': editable}
                      )

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_delete_target(request, listid, targetid):
    targetlist = get_object_or_404(TargetList, id=listid)
    target = get_object_or_404(Target, id=targetid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    tlist = targetlist.targets.filter(mail_address=target.mail_address)

    if not tlist:
        return render(request, 'Main/Campaigns/Targets/deletetarget.html',
                      {'targetlist': targetlist,
                      'target': target,
                      'notinlist': True}
                      )

    if request.method == "GET":
        return render(request, 'Main/Campaigns/Targets/deletetarget.html',
                      {'targetlist': targetlist,
                      'target': target}
                      )

    if request.method == "POST":

        targetlist.removeTarget(target)
        target.delete()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_list_targets_list(request, page=1):

    if request.method == "GET":
        visible_usrs = request.user.swordphishuser.visible_users()
        targetslists = TargetList.objects.filter(author__in=visible_usrs).order_by("-creation_date")

        paginator = Paginator(targetslists, 20)
        paginator.ELLIPSIS = ''

        try:
            lists = paginator.page(page)
        except PageNotAnInteger:
            lists = paginator.page(1)
        except EmptyPage:
            lists = paginator.page(paginator.num_pages)
        except Exception:
            lists = paginator.page(1)

        lists.pages = paginator.get_elided_page_range(page)

        return render(request, "Main/Campaigns/Targets/listtargetslists.html",
                      {'targetslists': lists,
                      "current_user": request.user.swordphishuser}
                      )

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_templates(request):
    return render(request, "Main/Campaigns/Templates/templates.html",
                  {"menuactive": "templates",
                  "types": Template.TEMPLATE_TYPE}
                  )


@validate_domain
@login_required
def campaign_create_template(request, typeid, duplicateid=None):

    phishform = None

    values = {}
    if duplicateid is not None:
        duplicate = get_object_or_404(Template, id=duplicateid)
        values = {"title": duplicate.title, "text": duplicate.text}

    if typeid == "1":
        phishform = SimpleMailForm(initial=values)
    elif typeid == "2":
        phishform = MailWithAttachmentForm(initial=values)
    elif typeid == "3":
        phishform = AttachmentForm(initial=values)
    elif typeid == "4":
        phishform = Redirection(initial=values)
    elif typeid == "5":
        phishform = Awareness(initial=values)
    elif typeid == "6":
        phishform = CredsHarvesterForm(initial=values)
    elif typeid == "7":
        phishform = FakeRansomForm(initial=values)
    else:
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'Main/Campaigns/Templates/createtemplate.html',
                      {"phishform": phishform,
                      "typeid": typeid}
                      )

    if request.method == "POST":

        if typeid == "1":
            phishform = SimpleMailForm(request.POST)
        elif typeid == "2":
            phishform = MailWithAttachmentForm(request.POST)
        elif typeid == "3":
            phishform = AttachmentForm(request.POST)
        elif typeid == "4":
            phishform = Redirection(request.POST)
        elif typeid == "5":
            phishform = Awareness(request.POST)
        elif typeid == "6":
            phishform = CredsHarvesterForm(request.POST)
        elif typeid == "7":
            phishform = FakeRansomForm(request.POST)
        else:
            return HttpResponseForbidden()

        if not phishform.is_valid():
            return render(request, 'Main/Campaigns/Templates/createtemplate.html',
                          {"phishform": phishform,
                          "typeid": typeid}
                          )

        pmail = Template.objects.filter(name=phishform.cleaned_data["name"],
                                        author=request.user.swordphishuser)

        if pmail:
            return render(request, 'Main/Campaigns/Templates/createtemplate.html',
                          {"phishform": phishform,
                          "typeid": typeid,
                          'template_already_exists': True}
                          )

        template = phishform.save(commit=False)
        template.author = request.user.swordphishuser
        template.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_edit_template(request, typeid, templateid):
    template = get_object_or_404(Template, id=templateid)

    if template.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    phishform = None

    if request.method == "GET":
        if typeid == "1":
            phishform = SimpleMailForm(instance=template)
        elif typeid == "2":
            phishform = MailWithAttachmentForm(instance=template)
        elif typeid == "3":
            phishform = AttachmentForm(instance=template)
        elif typeid == "4":
            phishform = Redirection(instance=template)
        elif typeid == "5":
            phishform = Awareness(instance=template)
        elif typeid == "6":
            phishform = CredsHarvesterForm(instance=template)
        elif typeid == "7":
            phishform = FakeRansomForm(instance=template)
        else:
            return HttpResponseForbidden()

        return render(request, 'Main/Campaigns/Templates/edittemplate.html',
                      {'phishform': phishform,
                      "typeid": typeid,
                      'templateid': templateid}
                      )

    if request.method == "POST":

        if typeid == "1":
            phishform = SimpleMailForm(request.POST, instance=template)
        elif typeid == "2":
            phishform = MailWithAttachmentForm(request.POST, instance=template)
        elif typeid == "3":
            phishform = AttachmentForm(request.POST, instance=template)
        elif typeid == "4":
            phishform = Redirection(request.POST, instance=template)
        elif typeid == "5":
            phishform = Awareness(request.POST, instance=template)
        elif typeid == "6":
            phishform = CredsHarvesterForm(request.POST, instance=template)
        elif typeid == "7":
            phishform = FakeRansomForm(request.POST, instance=template)
        else:
            return HttpResponseForbidden()

        if not phishform.is_valid():
            return render(request, 'Main/Campaigns/Templates/edittemplate.html',
                          {'phishform': phishform,
                          "typeid": typeid, 'templateid': templateid}
                          )

        result = Template.objects.filter(Q(name=phishform.cleaned_data["name"]) &
                                         Q(author=request.user.swordphishuser) &
                                         ~Q(id=template.id)
                                         )

        if result:
            return render(request, 'Main/Campaigns/Templates/edittemplate.html',
                          {'phishform': phishform,
                          "typeid": typeid,
                          'template_already_exists': True,
                          'templateid': templateid}
                          )

        template = phishform.save()
        template.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_delete_template(request, templateid):
    template = get_object_or_404(Template, id=templateid)

    if template.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'Main/Campaigns/Templates/deletetemplate.html',
                      {'template': template}
                      )

    if request.method == "POST":

        if template.is_used():
            return render(request, 'Main/Campaigns/Templates/deletetemplate.html',
                          {'template': template, 'templateused': True}
                          )

        template.delete()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_view_template(request, templateid):
    template = get_object_or_404(Template, id=templateid)

    if template.author not in request.user.swordphishuser.visible_users() and not template.public:
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'Main/Campaigns/Templates/viewtemplate.html', {'template': template})

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_list_template(request, page=1):

    if request.method == "GET":
        visible_users = request.user.swordphishuser.visible_users()
        templatelist = Template.objects.filter(Q(author__in=visible_users) |
                                               Q(public=True)).order_by("-creation_date")
        paginator = Paginator(templatelist, 20)
        paginator.ELLIPSIS = ''

        try:
            templates = paginator.page(page)
        except PageNotAnInteger:
            templates = paginator.page(1)
        except EmptyPage:
            templates = paginator.page(paginator.num_pages)
        except Exception:
            templates = paginator.page(1)

        templates.pages = paginator.get_elided_page_range(page)

        return render(request, 'Main/Campaigns/Templates/listtemplate.html',
                      {"templatelist": templates,
                      "current_user": request.user.swordphishuser}
                      )

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_campaigns(request):
    return render(request, "Main/Campaigns/Campaigns/campaigns.html",
                  {"menuactive": "campaigns",
                  "types": Campaign.CAMPAIGN_TYPES}
                  )


@validate_domain
@login_required
def campaign_running_campaigns(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    return render(request, "Main/Campaigns/Campaigns/running_campaigns.html",
                  {"types": Campaign.CAMPAIGN_TYPES}
                  )


@validate_domain
@login_required
def campaign_create_campaign(request, typeid, duplicateid=None):
    campaignform = None

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

        return render(request, 'Main/Campaigns/Campaigns/createcampaign.html',
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
            return render(request, 'Main/Campaigns/Campaigns/createcampaign.html',
                          {'campaignform': campaignform,
                          "typeid": typeid}
                          )

        existing = Campaign.objects.filter(name=campaignform.cleaned_data["name"],
                                           author=request.user.swordphishuser)

        if existing:
            return render(request, 'Main/Campaigns/Campaigns/createcampaign.html',
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


@validate_domain
@login_required
def campaign_test_campaign(request, campaignid):
    campaign = get_object_or_404(Campaign, id=campaignid)

    if campaign.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if request.method == "GET":
        campaignform = TestCampaignForm(instance=campaign)
        campaignform.fields["recipient"].initial = request.user.email

        return render(request, 'Main/Campaigns/Campaigns/testcampaign.html',
                      {'campaignform': campaignform,
                      'campaign': campaign}
                      )

    if request.method == "POST":

        campaignform = TestCampaignForm(request.POST, instance=campaign)
        if not campaignform.is_valid():
            return render(request, 'Main/Campaigns/Campaigns/testcampaign.html',
                          {'campaignform': campaignform,
                          'campaign': campaign}
                          )

        recipient = campaignform.cleaned_data["recipient"]

        try:
            campaign.test(recipient)
        except Exception as e:
            if hasattr(e, "errno"):
                if e.errno == errno.ECONNREFUSED:
                    return render(request, 'Main/Campaigns/Campaigns/testcampaign.html',
                                  {'campaignform': campaignform,
                                  'campaign': campaign,
                                  'connect_error': True}
                                  )
            else:
                raise e
        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_edit_campaign(request, typeid, campaignid):
    campaign = get_object_or_404(Campaign, id=campaignid)

    if campaign.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if campaign.status == "2":
        return HttpResponseForbidden()

    if request.method == "GET":

        campaignform = None

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

        return render(request, 'Main/Campaigns/Campaigns/editcampaign.html',
                      {'campaignform': campaignform,
                      "typeid": typeid,
                      'campaign': campaign}
                      )

    if request.method == "POST":
        campaignform = None

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
            return render(request, 'Main/Campaigns/Campaigns/editcampaign.html',
                          {'campaignform': campaignform,
                          "typeid": typeid,
                          'campaign': campaign}
                          )

        result = Campaign.objects.filter(Q(name=campaignform.cleaned_data["name"]) &
                                         Q(author=request.user.swordphishuser) &
                                         ~Q(id=campaign.id))

        if result:
            return render(request, 'Main/Campaigns/Campaigns/editcampaign.html',
                          {'campaignform': campaignform,
                          "typeid": typeid,
                          'campaign_already_exists': True}
                          )

        campaign = campaignform.save(commit=False)
        campaignform.save_m2m()
        campaign.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_delete_campaign(request, campaignid):
    campaign = get_object_or_404(Campaign, id=campaignid)

    if campaign.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if campaign.status == "2":
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'Main/Campaigns/Campaigns/deletecampaign.html',
                      {'campaign': campaign}
                      )

    if request.method == "POST":

        anons = campaign.anonymous_targets.all()
        for anon in anons:
            anon.delete()
        campaign.delete()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_list_campaigns(request, page=1):
    if request.method == "GET":
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

        return render(request, 'Main/Campaigns/Campaigns/listcampaigns.html',
                      {"campaignlist": campaigns,
                      "current_user": request.user.swordphishuser}
                      )

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_list_running_campaigns(request, page=1):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == "GET":
        campaignlist = Campaign.objects.filter(status="2").order_by("-start_date")
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

        return render(request, 'Main/Campaigns/Campaigns/list_running_campaigns.html',
                      {"campaignlist": campaigns,
                      "current_user": request.user.swordphishuser}
                      )

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_download_results(request, campaignid):
    campaign = get_object_or_404(Campaign, id=campaignid)

    if campaign.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if campaign.status != "3":
        return HttpResponseForbidden()

    if request.method == "GET" or request.method == "POST":
        excelmime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        data = None
        if exists('results/' + str(campaignid) + '.xlsx'):
            with open('results/' + str(campaignid) + '.xlsx', 'rb') as f:
                data = f.read()
        else:
            campaign.generate_results_xlsx()
            with open('results/' + str(campaignid) + '.xlsx', 'rb') as f:
                data = f.read()
        response = HttpResponse(data, content_type=excelmime)
        response['Content-Disposition'] = 'attachment; filename="%s_results.xlsx"' % campaign.name
        return response

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_display_dashboard(request, campaignid):
    campaign = get_object_or_404(Campaign, id=campaignid)

    if campaign.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if campaign.status != "2" and campaign.status != "3":
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'Main/Campaigns/Campaigns/dashboard.html', {"campaign": campaign})

    return HttpResponseForbidden()


@validate_domain
@login_required
def campaign_submit_reported_ids(request, campaignid):
    campaign = get_object_or_404(Campaign, id=campaignid)

    if campaign.status != "2" and campaign.status != "3":
        return HttpResponseForbidden()

    if request.method == "GET":
        reportform = ReportForm(instance=campaign)
        return render(request, 'Main/Campaigns/Campaigns/submit_reported_ids.html',
                      {"campaign": campaign,
                      "reportform": reportform}
                      )
    if request.method == "POST":
        regex = r'[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}'
        reportform = ReportForm(request.POST, instance=campaign)
        if not reportform.is_valid():
            return render(request, 'Main/Campaigns/Campaigns/submit_reported_ids.html',
                          {"campaign": campaign,
                          "reportform": reportform}
                          )
        text = reportform.cleaned_data['ids']
        ids = re.findall(regex, text)
        for i in ids:
            targetl = campaign.anonymous_targets.filter(uniqueid=i)
            if targetl:
                targetl[0].reported = True
                targetl[0].save()
        return HttpResponse("Ok")

    return HttpResponseForbidden()


# Admin Views
@validate_domain
@login_required
def admin_users(request):
    if request.user.swordphishuser.is_staff_or_admin():
        users_list = request.user.swordphishuser.subordinates()
        userform = UserForm()
        phishform = SwordphishUserForm()
        return render(request, 'Main/Admin/users.html',
                      {'newswordphishform': phishform,
                      'newuserform': userform,
                      "menuactive": "users",
                      "userslist": users_list}
                      )

    return HttpResponseForbidden()


@validate_domain
@login_required
def admin_entities(request):
    if request.user.swordphishuser.is_staff_or_admin():
        return render(request, "Main/Admin/entities.html", {"menuactive": "entities"})

    return HttpResponseForbidden()


@validate_domain
@login_required
def admin_regions(request):
    if request.user.swordphishuser.is_staff_or_admin():
        return render(request, "Main/Admin/regions.html", {"menuactive": "regions"})

    return HttpResponseForbidden()


def campaign_display_awareness(request, campaignid, targetid):
    campaigntest = Campaign.objects.filter(testid=targetid)

    if campaigntest:
        campaign = campaigntest[0]
    else:
        campaign = get_object_or_404(Campaign, id=campaignid)
        target = get_object_or_404(AnonymousTarget, uniqueid=targetid)

        if campaign.campaign_type == "3" or campaign.campaign_type == "4":
            if campaign.status == "2":
                target.form_submitted = True
                target.form_submitted_time = datetime.now(tz=get_current_timezone())
                target.save()

    if campaign.onclick_action.template_type == "4":
        return redirect(campaign.onclick_action.title)

    if campaign.onclick_action.template_type == "5":
        if "HTTP_USER_AGENT" in request.META:
            if "MSIE" in request.META["HTTP_USER_AGENT"]:
                template = internet_explorer_img_hack_template(campaign.onclick_action)
                return render(request, "Main/awareness.html", {"template": template})

            return render(request, "Main/awareness.html",
                          {"template": campaign.onclick_action.text}
                          )
    else:
        return HttpResponseNotFound()

    return HttpResponseForbidden()


def campaign_target_click(request, targetid):
    campaigntest = Campaign.objects.filter(testid=targetid)
    test = False

    if campaigntest:
        test = True
        campaign = campaigntest[0]
    else:
        target = get_object_or_404(AnonymousTarget, uniqueid=targetid)

        if target.campaign_set.count() > 0:
            campaign = target.campaign_set.get()
        else:
            return HttpResponseNotFound()

        if campaign.status == "2":
            tar = campaign.anonymous_targets.filter(uniqueid=targetid)

            if not tar:
                return HttpResponseForbidden()

            target.link_clicked = True
            target.mail_opened = True
            target.link_clicked_time = datetime.now(tz=get_current_timezone())
            if not target.mail_opened_time:
                target.mail_opened_time = datetime.now(tz=get_current_timezone())
            target.save()

    if campaign.status != "2" and not test:
        return campaign_display_awareness(request, campaign.id, targetid)

    if campaign.campaign_type == "1":
        if campaign.onclick_action.template_type == "4":
            return redirect(campaign.onclick_action.title)
        if campaign.onclick_action.template_type == "5":
            if "HTTP_USER_AGENT" in request.META:
                if "MSIE" in request.META["HTTP_USER_AGENT"]:
                    template = internet_explorer_img_hack_template(campaign.onclick_action)
                    return render(request, "Main/awareness.html", {"template": template})
                return render(request, "Main/awareness.html",
                              {"template": campaign.onclick_action.text}
                              )
        else:
            return HttpResponseNotFound()

    if campaign.campaign_type == "3":

        template = campaign.fake_form.text

        if "HTTP_USER_AGENT" in request.META:
            if "MSIE" in request.META["HTTP_USER_AGENT"]:
                template = internet_explorer_img_hack_template(campaign.fake_form)

        soup = BeautifulSoup(template, "html.parser")
        forms = soup.findAll("form")

        for form in forms:
            form["onsubmit"] = "return false;"

        submits = soup.findAll("input", attrs={"type": "submit"})

        if campaign.onclick_action.template_type in ["4", "5"]:
            for submit in submits:
                url = reverse('Main:campaign_display_awareness',
                              kwargs={'campaignid': campaign.id, 'targetid': targetid}
                              )
                submit["onclick"] = "window.location.replace('%s');" % url

        return render(request, "Main/awareness.html", {"template": str(soup)})

    if campaign.campaign_type == "4":
        template = campaign.fake_ransom.text
        if "HTTP_USER_AGENT" in request.META:
            if "MSIE" in request.META["HTTP_USER_AGENT"]:
                template = internet_explorer_img_hack_template(campaign.fake_ransom)

        if campaign.onclick_action.template_type in ["4", "5"]:
            linkurl = reverse('Main:campaign_display_awareness',
                              kwargs={'campaignid': campaign.id, 'targetid': targetid})
            template = template.replace("FIXMEURL", linkurl)

        return render(request, "Main/awareness.html", {"template": template})

    return HttpResponseForbidden()


def campaign_target_openmail(request, targetid):
    # pylint: disable=W0613
    campaigntest = Campaign.objects.filter(testid=targetid)

    if campaigntest:
        campaign = campaigntest[0]
    else:
        target = get_object_or_404(AnonymousTarget, uniqueid=targetid)

        if target.campaign_set.count() > 0:
            campaign = target.campaign_set.get()
        else:
            return HttpResponseNotFound()

        if campaign.status == "2":
            test = campaign.anonymous_targets.filter(uniqueid=targetid)

            if not test:
                return HttpResponseForbidden()

            target.mail_opened = True
            target.mail_opened_time = datetime.now(tz=get_current_timezone())
            target.save()

    blank = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABC\
            AMAAAAoyzS7AAAABGdBTUEAALGPC/xhBQAAAAFzUkdC\
            AK7OHOkAAAADUExURQAAAKd6PdoAAAABdFJOUwBA5thm\
            AAAACklEQVQI12NgAAAAAgAB4iG8MwAAAABJRU5ErkJggg=="

    return HttpResponse(b64decode(blank), content_type='image/gif')


def campaign_target_reportmail(request, targetid):
    # pylint: disable=W0613
    target = get_object_or_404(AnonymousTarget, uniqueid=targetid)

    if target.campaign_set.count() > 0:
        campaign = target.campaign_set.get()
    else:
        return HttpResponseNotFound()

    if campaign.status == "2":
        test = campaign.anonymous_targets.filter(uniqueid=targetid)

        if not test:
            return HttpResponseForbidden()

        target.reported = True
        target.reported_time = datetime.now(tz=get_current_timezone())
        target.save()

    return HttpResponse("Ok")


def campaign_target_openattachment(request, targetid):
    # pylint: disable=W0613
    campaigntest = Campaign.objects.filter(testid=targetid)

    if campaigntest:
        campaign = campaigntest[0]
    else:
        target = get_object_or_404(AnonymousTarget, uniqueid=targetid)

        if target.campaign_set.count() > 0:
            campaign = target.campaign_set.get()
        else:
            return HttpResponseNotFound()

        if campaign.status == "2":

            test = campaign.anonymous_targets.filter(uniqueid=targetid)

            if not test:
                return HttpResponseForbidden()

            target.attachment_opened = True
            target.attachment_opened_time = datetime.now(tz=get_current_timezone())
            target.save()

    blank = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABC\
            AMAAAAoyzS7AAAABGdBTUEAALGPC/xhBQAAAAFzUkdC\
            AK7OHOkAAAADUExURQAAAKd6PdoAAAABdFJOUwBA5thm\
            AAAACklEQVQI12NgAAAAAgAB4iG8MwAAAABJRU5ErkJggg=="

    return HttpResponse(b64decode(blank), content_type='image/gif')


@validate_domain
def doc(request):
    # pylint: disable=W0613
    return redirect("static/swordphish_documentation.pdf")


def domains_feed(request):
    # pylint: disable=W0613
    domains = PhishmailDomain.objects.all()
    res = json.dumps([{"domain": o.domain} for o in domains])
    return HttpResponse(res)


def internet_explorer_img_hack_template(template):
    soup = BeautifulSoup(template.text)

    for img in soup.findAll("img"):
        imgid = img["id"]
        img["src"] = reverse("getimage", args=[template.id, imgid], urlconf="Main.urls")

    return str(soup)


def internet_explorer_img_hack(request, templateid, imgid):
    # pylint: disable=W0613
    template = get_object_or_404(Template, id=templateid)

    soup = BeautifulSoup(template.text, "html.parser")
    img = soup.find("img", {"id": imgid})

    if img is not None:
        tmp = img["src"].split(',')
        imgsrc = tmp[1]
        mime = tmp[0].split(';')[0].split(':')[1]
        return HttpResponse(b64decode(imgsrc), content_type=mime)

    return HttpResponseNotFound()
