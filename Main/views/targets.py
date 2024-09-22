from zipfile import BadZipfile

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import ValidationError
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError

from Main.core.targets import export_to_xlsx, load_targets_from_excel
from Main.forms import TargetsListForm, NewTargetForm, AttributeForm
from Main.models import TargetList, Target


@login_required
def get_targets(request):
    return render(request, "Main/Targets/targets.html", {"menuactive": "targets"})


@login_required
def create_targets_list(request):
    if request.method == "GET":
        targetlistform = TargetsListForm()
        return render(request, 'Main/Targets/newtargetslist.html',
                      {'targetlistform': targetlistform}
                      )

    if request.method == "POST":
        targetlistform = TargetsListForm(request.POST)

        if not targetlistform.is_valid():
            return render(request, 'Main/Targets/newtargetslist.html',
                          {'targetlistform': targetlistform}
                          )

        if TargetList.objects.filter(name=targetlistform.cleaned_data["name"],
                                     author=request.user.swordphishuser):
            return render(request, 'Main/Targets/newtargetslist.html',
                          {'targetlistform': targetlistform,
                           'list_already_exists': True}
                          )

        targetlist = targetlistform.save(commit=False)
        targetlist.author = request.user.swordphishuser
        targetlist.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def delete_targets_list(request, listid):
    targetlist = get_object_or_404(TargetList, id=listid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'Main/Targets/deletetargetslist.html',
                      {'targetlist': targetlist}
                      )

    if request.method == "POST":
        if targetlist.is_used():
            return render(request, 'Main/Targets/deletetargetslist.html',
                          {'targetlist': targetlist, 'targetlistused': True}
                          )
        targetlist.targets.all().delete()
        targetlist.delete()
        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def edit_targets_list(request, listid):
    targetlist = get_object_or_404(TargetList, id=listid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if request.method == "GET":
        targetlistform = TargetsListForm(instance=targetlist)
        return render(request, 'Main/Targets/edittargetslist.html',
                      {'targetlistform': targetlistform,
                       'listid': listid}
                      )

    if request.method == "POST":
        targetlistform = TargetsListForm(request.POST)

        if not targetlistform.is_valid():
            return render(request, 'Main/Targets/edittargetslist.html',
                          {'targetlistform': targetlistform,
                           'listid': listid}
                          )

        if TargetList.objects.filter(name=targetlistform.cleaned_data["name"],
                                     author=request.user.swordphishuser):
            return render(request, 'Main/Targets/edittargetslist.html',
                          {'targetlistform': targetlistform,
                           'list_already_exists': True,
                           'listid': listid}
                          )

        targetlist.name = targetlistform.cleaned_data["name"]
        targetlist.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def import_targets_list(request, listid):
    targetlist = get_object_or_404(TargetList, id=listid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'Main/Targets/importtargetslist.html',
                      {'targetlist': targetlist,
                       'listid': listid}
                      )

    if request.method == "POST":

        try:
            f = request.FILES['targetlist']
        except MultiValueDictKeyError:
            return render(request, 'Main/Targets/importtargetslist.html',
                          {'targetlist': targetlist,
                           'listid': listid,
                           'bad_format_file': True}
                          )

        try:
            load_targets_from_excel(targetlist, f)
        except BadZipfile:
            return render(request, 'Main/Targets/importtargetslist.html',
                          {'targetlist': targetlist,
                           'listid': listid,
                           'bad_file': True}
                          )
        except ValidationError as e:
            return render(request, 'Main/Targets/importtargetslist.html',
                          {'targetlist': targetlist,
                           'listid': listid,
                           'bademail': True,
                           'exception': e}
                          )
        except Exception:
            return render(request, 'Main/Targets/importtargetslist.html',
                          {'targetlist': targetlist,
                           'listid': listid,
                           'unknown_error': True})

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def export_targets_list(request, listid):
    targetlist = get_object_or_404(TargetList, id=listid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    if request.method == "GET" or request.method == "POST":
        excelmime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(export_to_xlsx(targetlist), content_type=excelmime)
        response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % targetlist.name
        return response

    return HttpResponseForbidden()


@login_required
def create_target(request, listid):
    targetlist = get_object_or_404(TargetList, id=listid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    targetform = NewTargetForm()
    attributeformset = formset_factory(AttributeForm, extra=0)

    if request.method == "GET":
        return render(request, 'Main/Targets/createtarget.html',
                      {'targetlist': targetlist,
                       'targetform': targetform,
                       'attributeformset': attributeformset,
                       'listid': listid}
                      )

    if request.method == "POST":
        targetform = NewTargetForm(request.POST)
        attributeformset = attributeformset(request.POST)

        if (not targetform.is_valid()) or (not attributeformset.is_valid()):
            return render(request, 'Main/Targets/createtarget.html',
                          {'targetlist': targetlist,
                           'targetform': targetform,
                           'attributeformset': attributeformset,
                           'listid': listid}
                          )

        existing = targetlist.targets.filter(mail_address=targetform.cleaned_data["mail_address"])

        if existing:
            return render(request, 'Main/Targets/createtarget.html',
                          {'targetlist': targetlist,
                           'targetform': targetform,
                           'attributeformset': attributeformset,
                           'listid': listid,
                           'target_already_exists': True}
                          )

        newtarget = targetform.save()

        for attform in attributeformset:
            if "key" in attform.cleaned_data.keys() and "value" in attform.cleaned_data.keys():
                newtarget.add_attribute(attform.cleaned_data["key"], attform.cleaned_data["value"])

        targetlist.targets.add(newtarget)

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def edit_target(request, listid, targetid):
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
        return render(request, 'Main/Targets/edittarget.html',
                      {'targetlist': targetlist,
                       'targetid': targetid,
                       'targetform': targetform,
                       'attformset': attformset}
                      )

    if request.method == "POST":
        targetform = NewTargetForm(request.POST)
        attformset = formset(request.POST)

        if not (targetform.is_valid() and attformset.is_valid()):
            return render(request, 'Main/Targets/edittarget.html',
                          {'targetlist': targetlist,
                           'targetid': targetid,
                           'targetform': targetform,
                           'attformset': attformset}
                          )

        tl = targetlist.targets.filter(mail_address=targetform.cleaned_data["mail_address"])

        for tar in tl:
            if tar.id != target.id:
                return render(request, 'Main/Targets/edittarget.html',
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
            target.add_attribute(attform.cleaned_data["key"], attform.cleaned_data["value"])

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def list_targets(request, listid, page=1):
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
    except:
        targets = paginator.page(1)

    targets.pages = paginator.get_elided_page_range(page)

    if request.method == "GET":
        return render(request, 'Main/Targets/listtargets.html',
                      {'targetlist': targetlist,
                       'targets': targets,
                       'listname': targetlist.name,
                       'listid': listid,
                       'editable': editable}
                      )

    return HttpResponseForbidden()


@login_required
def delete_target(request, listid, targetid):
    targetlist = get_object_or_404(TargetList, id=listid)
    target = get_object_or_404(Target, id=targetid)

    if targetlist.author not in request.user.swordphishuser.visible_users():
        return HttpResponseForbidden()

    tlist = targetlist.targets.filter(mail_address=target.mail_address)

    if not tlist:
        return render(request, 'Main/Targets/deletetarget.html',
                      {'targetlist': targetlist,
                       'target': target,
                       'notinlist': True}
                      )

    if request.method == "GET":
        return render(request, 'Main/Targets/deletetarget.html',
                      {'targetlist': targetlist,
                       'target': target}
                      )

    if request.method == "POST":
        targetlist.remove_target(target)
        target.delete()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def list_targets_list(request, page=1):
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

        return render(request, "Main/Targets/listtargetslists.html",
                      {'targetslists': lists,
                       "current_user": request.user.swordphishuser}
                      )

    return HttpResponseForbidden()
