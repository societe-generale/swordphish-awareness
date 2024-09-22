from json import dumps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect

from Main.models import PhishmailDomain


@login_required
def index(request):
    return redirect("Main:get_campaigns")


def domains_feed(request):
    domains = PhishmailDomain.objects.all()
    res = dumps([{"domain": o.domain} for o in domains])
    return HttpResponse(res)
