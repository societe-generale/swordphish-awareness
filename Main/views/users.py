from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

from LocalUsers.forms import SwordphishUserForm, UserForm


@login_required
def users(request):
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


@login_required
def entities(request):
    if request.user.swordphishuser.is_staff_or_admin():
        return render(request, "Main/Admin/entities.html", {"menuactive": "entities"})

    return HttpResponseForbidden()


@login_required
def regions(request):
    if request.user.swordphishuser.is_staff_or_admin():
        return render(request, "Main/Admin/regions.html", {"menuactive": "regions"})

    return HttpResponseForbidden()
