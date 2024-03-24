from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render

from LocalUsers.forms import AddAdminForm, RegionForm, AddUserInRegionForm
from LocalUsers.forms import EntityForm, EditMyProfileForm
from LocalUsers.forms import SwordphishUserForm, CreateUserForm, UserForm
from LocalUsers.models import SwordphishUser, Entity, Region, RegionMembership


def __send_user_informations(firstname, email, password, creator):
    template = settings.NEW_ACCOUNT_TEMPLATE % (firstname,
                                                settings.SWORPDHISH_URL,
                                                email,
                                                password)

    if creator.lower() == settings.USER_ACCOUNT_CREATION_MAIL_CONTACT:
        message = EmailMessage(from_email=settings.USER_ACCOUNT_CREATION_MAIL_SENDER,
                               subject=settings.USER_ACCOUNT_CREATION_MAIL_TITLE,
                               body=template,
                               to=[email],
                               cc=[settings.USER_ACCOUNT_CREATION_MAIL_CONTACT],
                               reply_to=[settings.USER_ACCOUNT_CREATION_MAIL_CONTACT])
    else:
        message = EmailMessage(from_email=settings.USER_ACCOUNT_CREATION_MAIL_SENDER,
                               subject=settings.USER_ACCOUNT_CREATION_MAIL_TITLE,
                               body=template,
                               to=[email],
                               cc=[settings.USER_ACCOUNT_CREATION_MAIL_CONTACT, creator],
                               reply_to=[settings.USER_ACCOUNT_CREATION_MAIL_CONTACT])
    message.send()


def __lost_password(firstname, email, password):
    template = settings.LOST_PASSWORD_TEMPLATE % (firstname,
                                                  settings.SWORPDHISH_URL,
                                                  email,
                                                  password)

    message = EmailMessage(from_email=settings.USER_ACCOUNT_CREATION_MAIL_SENDER,
                           subject=settings.USER_ACCOUNT_LOST_PASS_MAIL_TITLE,
                           body=template,
                           to=[email],
                           cc=[settings.USER_ACCOUNT_CREATION_MAIL_CONTACT],
                           reply_to=[settings.USER_ACCOUNT_CREATION_MAIL_CONTACT])
    message.send()


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            if request.POST.get('remember', None):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(600)
            if user.is_active:
                login(request, user)
                return redirect('Main:index')
            return render(request, 'LocalUsers/index.html', {'error': 'error'})
        else:
            return render(request, 'LocalUsers/index.html', {'error': 'error'})
    else:
        if request.user.is_authenticated:
            return redirect('Main:index')
        return render(request, "LocalUsers/index.html")


@login_required
def myprofile(request):
    if request.method == "GET":
        userform = EditMyProfileForm(instance=request.user)
        swordphishuser = SwordphishUserForm(instance=request.user.swordphishuser)
        return render(request, "LocalUsers/editprofile.html",
                      {'userform': userform, 'swordphishform': swordphishuser})

    if request.method == "POST":
        userform = EditMyProfileForm(request.POST, instance=request.user)
        swordphishuser = SwordphishUserForm(request.POST, instance=request.user.swordphishuser)
        if userform.is_valid() and swordphishuser.is_valid():
            editeduser = userform.save(commit=False)

            if userform.cleaned_data["password_confirmation"] != "":
                editeduser.set_password(userform.cleaned_data["password_confirmation"])
                update_session_auth_hash(request, editeduser)

            editeduser.save()
            editedswordphishuser = swordphishuser.save(commit=False)
            editedswordphishuser.must_change_password = False
            editedswordphishuser.save()
            return HttpResponse("Ok")

        return render(request, "LocalUsers/editprofile.html",
                      {'userform': userform, 'swordphishform': swordphishuser})

    return HttpResponseForbidden()


def user_logout(request):
    logout(request)
    return redirect('Authent:login')


@login_required
def block_unblock_user(request, userid=None):
    user = get_object_or_404(SwordphishUser, id=userid)

    if not user.can_be_edited(request.user):
        return HttpResponseForbidden()

    if user.user.is_active:
        user.user.is_active = False
        user.user.save()
    else:
        user.user.is_active = True
        user.user.save()

    return HttpResponse("Ok")


@login_required
def edit_user(request, userid=None):
    user = get_object_or_404(SwordphishUser, id=userid)
    usermail = user.user.username

    if not user.can_be_edited(request.user):
        return HttpResponseForbidden()

    if request.method == "GET":
        userform = UserForm(instance=user.user)
        phishform = SwordphishUserForm(instance=user)
        return render(request, 'LocalUsers/edituser.html',
                      {
                          'swordphishform': phishform,
                          'userform': userform,
                          'userid': userid
                      })

    if request.method == "POST":
        userform = UserForm(request.POST, instance=user.user)
        swordphishform = SwordphishUserForm(request.POST, instance=user)

        if not userform.is_valid():
            return render(request, 'LocalUsers/edituser.html',
                          {
                              'swordphishform': swordphishform,
                              'userform': userform,
                              'userid': userid
                          })

        if not swordphishform.is_valid():
            return render(request, 'LocalUsers/edituser.html',
                          {
                              'swordphishform': swordphishform,
                              'userform': userform,
                              'userid': userid
                          })

        if userform.cleaned_data["email"] != usermail:
            if User.objects.filter(email=userform.cleaned_data["email"]).count() > 0:
                return render(request, 'LocalUsers/newuser.html',
                              {
                                  'swordphishform': swordphishform,
                                  'userform': userform,
                                  'user_already_exists': True
                              })

        newuser = userform.save(commit=False)
        newuser.username = userform.cleaned_data["email"].lower()
        newuser.save()
        swordphishform.save()

        password = request.POST.get("password", "")
        password_confirmation = request.POST.get("password_confirmation", "")

        if password != "" and password == password_confirmation:
            user.user.set_password(password)
            if user.user != request.user:
                user.must_change_password = True
                user.save()

        user.user.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def new_user(request):
    if not request.user.swordphishuser.is_staff_or_admin():
        return HttpResponseForbidden()

    if request.method == "GET":
        userform = CreateUserForm()
        phishform = SwordphishUserForm()
        return render(request, 'LocalUsers/newuser.html',
                      {
                          'swordphishform': phishform,
                          'userform': userform
                      })

    if request.method == "POST":
        userform = CreateUserForm(request.POST)
        phishform = SwordphishUserForm(request.POST)

        if not request.user.swordphishuser.is_staff_or_admin():
            return HttpResponseForbidden()

        if not userform.is_valid():
            return render(request, 'LocalUsers/newuser.html',
                          {
                              'swordphishform': phishform,
                              'userform': userform
                          })

        if User.objects.filter(email=userform.cleaned_data["email"]):
            return render(request, 'LocalUsers/newuser.html',
                          {
                              'swordphishform': phishform,
                              'userform': userform,
                              'user_already_exists': True
                          })

        if not phishform.is_valid():
            return render(request, 'LocalUsers/newuser.html',
                          {
                              'swordphishform': phishform,
                              'userform': userform
                          })

        user = userform.save(commit=False)
        user.username = userform.cleaned_data["email"].lower()
        password = User.objects.make_random_password()
        user.set_password(password)
        user.save()
        user.swordphishuser.phone_number = phishform.cleaned_data["phone_number"]
        user.swordphishuser.must_change_password = True
        user.swordphishuser.save()

        __send_user_informations(userform.cleaned_data["first_name"],
                                 userform.cleaned_data["email"],
                                 password, request.user.email
                                 )

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def list_users(request, emailcontains=None):
    if not request.user.swordphishuser.is_staff_or_admin():
        return HttpResponseForbidden()

    if emailcontains is not None:
        users_list = SwordphishUser.objects.filter(user__email__contains=emailcontains)
    else:
        users_list = SwordphishUser.objects.all()
    full_list = []
    for user in users_list:
        full_list.append((user, user.can_be_edited(request.user)))
    return render(request, 'LocalUsers/listusers.html',
                  {
                      "userslist": full_list,
                      "current_user": request.user
                  })


@login_required
def new_entity(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == "GET":
        entityform = EntityForm()
        return render(request, 'LocalUsers/newentity.html', {'entityform': entityform})

    if request.method == "POST":
        entityform = EntityForm(request.POST)
        if not entityform.is_valid():
            return render(request, 'LocalUsers/newentity.html', {'entityform': entityform})

        if Entity.objects.filter(name=entityform.cleaned_data["name"]):
            return render(request, 'LocalUsers/newentity.html',
                          {
                              'entityform': entityform,
                              'entity_already_exists': True
                          })

        entityform.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def edit_entity(request, entityid=None):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    entities = request.user.swordphishuser.entities()
    entity = get_object_or_404(Entity, id=entityid)

    if entity not in entities:
        return HttpResponseForbidden()

    if request.method == "GET":
        entityform = EntityForm(instance=entity)
        return render(request, 'LocalUsers/editentity.html',
                      {
                          'entityform': entityform,
                          "entityid": entityid
                      })

    if request.method == "POST":
        entityform = EntityForm(request.POST)
        if not entityform.is_valid():
            return render(request, 'LocalUsers/editentity.html',
                          {
                              'entityform': entityform,
                              "entityid": entityid
                          })

        if Entity.objects.filter(name=entityform.cleaned_data["name"]):
            return render(request, 'LocalUsers/editentity.html',
                          {
                              'entityform': entityform,
                              'entity_already_exists': True,
                              "entityid": entityid
                          })

        entity.name = entityform.cleaned_data["name"]
        entity.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def list_entities(request):
    if not request.user.swordphishuser.is_staff_or_admin():
        return HttpResponseForbidden()

    entity_list = request.user.swordphishuser.entities()
    return render(request, 'LocalUsers/listentity.html', {"entitylist": entity_list})


@login_required
def list_entity_admins(request, entityid):
    entities = request.user.swordphishuser.entities()
    entity = get_object_or_404(Entity, id=entityid)

    if not request.user.swordphishuser.is_staff_or_admin():
        return HttpResponseForbidden()

    if entity not in entities:
        return HttpResponseForbidden()
    admin_list = entity.admins.all()
    return render(request, 'LocalUsers/listentityadmins.html',
                  {
                      "userslist": admin_list,
                      "entityid": entityid
                  })


@login_required
def add_entity_admin(request, entityid):
    entity = get_object_or_404(Entity, id=entityid)
    entities = request.user.swordphishuser.entities()

    if not request.user.swordphishuser.is_staff_or_admin():
        return HttpResponseForbidden()

    if entity not in entities:
        return HttpResponseForbidden()

    if request.method == "GET":
        adminform = AddAdminForm(instance=entity)
        return render(request, 'LocalUsers/addentityadmin.html',
                      {
                          'adminform': adminform,
                          'entityid': entityid
                      })

    if request.method == "POST":
        addform = AddAdminForm(request.POST, instance=entity)
        if addform.is_valid():
            newadmin = SwordphishUser.objects.get(pk=addform.cleaned_data["users"])
            entity.admins.add(newadmin)
            entity.save()
            return HttpResponse("Ok")

        return render(request, 'LocalUsers/addentityadmin.html',
                      {
                          'adminform': addform,
                          'entityid': entityid
                      })

    return HttpResponseForbidden()


@login_required
def remove_entity_admin(request, entityid, adminid):
    entity = get_object_or_404(Entity, id=entityid)
    admin = get_object_or_404(SwordphishUser, id=adminid)
    entities = request.user.swordphishuser.entities()

    if not request.user.swordphishuser.is_staff_or_admin():
        return HttpResponseForbidden()

    if entity not in entities:
        return HttpResponseForbidden()

    if adminid == request.user.swordphishuser.id:
        return render(request, 'LocalUsers/removeentityadmin.html',
                      {
                          'entity': entity,
                          'admin': admin,
                          'not_entity_admin': True
                      })

    if request.method == "GET":
        return render(request, 'LocalUsers/removeentityadmin.html',
                      {
                          'entity': entity,
                          'admin': admin
                      })

    if request.method == "POST":
        entity.admins.remove(admin)
        entity.save()
        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def new_region(request):
    if not request.user.swordphishuser.is_staff_or_admin():
        return HttpResponseForbidden()

    if request.method == "GET":
        regionform = RegionForm(current_user=request.user)
        return render(request, 'LocalUsers/newregion.html', {'regionform': regionform})

    if request.method == "POST":
        regionform = RegionForm(request.POST, current_user=request.user)
        if not regionform.is_valid():
            return render(request, 'LocalUsers/newregion.html', {'regionform': regionform})

        entity = Entity.objects.get(pk=regionform.cleaned_data["entity"])

        if entity not in request.user.swordphishuser.entities():
            return HttpResponseForbidden()

        if Region.objects.filter(name=regionform.cleaned_data["name"], entity=entity):
            return render(request, 'LocalUsers/newregion.html',
                          {
                              'regionform': regionform,
                              'region_already_exists': True
                          })

        region = regionform.save(commit=False)
        region.entity = entity
        region.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def edit_region(request, regionid):
    regions = request.user.swordphishuser.regions()
    region = get_object_or_404(Region, id=regionid)

    if not request.user.swordphishuser.is_staff_or_admin():
        return HttpResponseForbidden()

    if region not in regions:
        return HttpResponseForbidden()

    if request.method == "GET":
        regionform = RegionForm(instance=region, current_user=request.user)
        return render(request, 'LocalUsers/editregion.html',
                      {
                          'regionform': regionform,
                          "regionid": regionid
                      })

    if request.method == "POST":
        regionform = RegionForm(request.POST, current_user=request.user)
        if not regionform.is_valid():
            return render(request, 'LocalUsers/editregion.html',
                          {
                              'regionform': regionform,
                              "regionid": regionid
                          })

        entity = Entity.objects.get(pk=regionform.cleaned_data["entity"])

        if Region.objects.filter(name=regionform.cleaned_data["name"], entity=entity):
            return render(request, 'LocalUsers/editregion.html',
                          {
                              'regionform': regionform,
                              'region_already_exists': True,
                              "regionid": regionid
                          })

        region.name = regionform.cleaned_data["name"]
        region.entity = entity
        region.save()

        return HttpResponse("Ok")

    return HttpResponseForbidden()


@login_required
def list_regions(request):
    if not request.user.swordphishuser.is_staff_or_admin():
        return HttpResponseForbidden()

    region_list = request.user.swordphishuser.regions()
    return render(request, 'LocalUsers/listregion.html', {"regionlist": region_list})


@login_required
def list_region_users(request, regionid):
    regions = request.user.swordphishuser.regions()
    region = get_object_or_404(Region, id=regionid)

    if not request.user.swordphishuser.is_staff_or_admin():
        return HttpResponseForbidden()

    if region not in regions:
        return HttpResponseForbidden()

    members = region.members.all()

    return render(request, 'LocalUsers/listregionsusers.html',
                  {
                      "userslist": members,
                      "regionid": regionid
                  })


@login_required
def add_region_user(request, regionid):
    region = get_object_or_404(Region, id=regionid)
    regions = request.user.swordphishuser.regions()

    if not request.user.swordphishuser.is_staff_or_admin():
        return HttpResponseForbidden()

    if region not in regions:
        return HttpResponseForbidden()

    if request.method == "GET":
        userregionform = AddUserInRegionForm(instance=region)
        return render(request, 'LocalUsers/adduserinregion.html',
                      {
                          'userregionform': userregionform,
                          'regionid': regionid
                      })

    if request.method == "POST":
        userregionform = AddUserInRegionForm(request.POST, instance=region)
        if userregionform.is_valid():
            newuser = SwordphishUser.objects.get(pk=userregionform.cleaned_data["users"])
            membership = RegionMembership(region=region, user=newuser)
            membership.save()
            return HttpResponse("Ok")

        return render(request, 'LocalUsers/adduserinregion.html',
                      {
                          'userregionform': userregionform,
                          'regionid': regionid
                      })

    return HttpResponseForbidden()


@login_required
def remove_region_user(request, regionid, userid):
    region = get_object_or_404(Region, id=regionid)
    user = get_object_or_404(SwordphishUser, id=userid)
    regions = request.user.swordphishuser.regions()

    if not request.user.swordphishuser.is_staff_or_admin():
        return HttpResponseForbidden()

    if region not in regions:
        return HttpResponseForbidden()

    if request.method == "GET":
        return render(request, 'LocalUsers/removeuserinregion.html',
                      {
                          'region': region,
                          'user': user
                      })

    if request.method == "POST":
        RegionMembership.objects.filter(region=region, user=user).delete()
        return HttpResponse("Ok")

    return HttpResponseForbidden()
