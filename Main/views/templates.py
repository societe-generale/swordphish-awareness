from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET

from Main.forms import AttachmentForm, Redirection, Awareness, CredsHarvesterForm
from Main.forms import FakeRansomForm, SimpleMailForm, MailWithAttachmentForm
from Main.models import Template


@login_required
@require_GET
def get_templates(request):
    return render(request, "Main/Templates/templates.html",
                  {"menuactive": "templates",
                   "types": Template.TEMPLATE_TYPE})


@login_required
def create_template(request, typeid, duplicateid=None):
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
        return render(request, 'Main/Templates/createtemplate.html',
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
            return render(request, 'Main/Templates/createtemplate.html',
                          {"phishform": phishform,
                           "typeid": typeid}
                          )

        pmail = Template.objects.filter(name=phishform.cleaned_data["name"],
                                        author=request.user.swordphishuser)

        if pmail:
            return render(request, 'Main/Templates/createtemplate.html',
                          {"phishform": phishform,
                           "typeid": typeid,
                           'template_already_exists': True}
                          )

        template = phishform.save(commit=False)
        template.author = request.user.swordphishuser
        template.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def edit_template(request, templateid):
    template = get_object_or_404(Template, id=templateid)
    typeid = template.template_type

    if template.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

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

        return render(request, 'Main/Templates/edittemplate.html',
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
            return render(request, 'Main/Templates/edittemplate.html',
                          {'phishform': phishform,
                           "typeid": typeid, 'templateid': templateid}
                          )

        result = Template.objects.filter(Q(name=phishform.cleaned_data["name"]) &
                                         Q(author=request.user.swordphishuser) &
                                         ~Q(id=template.id)
                                         )

        if result:
            return render(request, 'Main/Templates/edittemplate.html',
                          {'phishform': phishform,
                           "typeid": typeid,
                           'template_already_exists': True,
                           'templateid': templateid}
                          )

        template = phishform.save()
        template.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def delete_template(request, templateid):
    template = get_object_or_404(Template, id=templateid)

    if template.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'Main/Templates/deletetemplate.html',
                      {'template': template}
                      )

    if request.method == "POST":

        if template.is_used():
            return render(request, 'Main/Templates/deletetemplate.html',
                          {'template': template, 'templateused': True}
                          )

        template.delete()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def view_template(request, templateid):
    template = get_object_or_404(Template, id=templateid)

    if template.author not in request.user.swordphishuser.visible_users() and not template.public:
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'Main/Templates/viewtemplate.html', {'template': template})

    return HttpResponseForbidden()


@login_required
@require_GET
def list_template(request, page=1):
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

    return render(request, 'Main/Templates/listtemplate.html',
                  {"templatelist": templates,
                   "current_user": request.user.swordphishuser})
