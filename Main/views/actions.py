from base64 import b64decode
from datetime import datetime

from bs4 import BeautifulSoup
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.timezone import get_current_timezone

from Main.models import AnonymousTarget, Campaign, Template


def display_awareness(request, targetid):
    campaigntest = Campaign.objects.filter(testid=targetid)

    if campaigntest:
        campaign = campaigntest[0]
    else:
        target = get_object_or_404(AnonymousTarget, uniqueid=targetid)
        campaign = get_object_or_404(Campaign, id=target.campaign_set.get())

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


def target_click(request, targetid):
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
        return display_awareness(request, campaign.id, targetid)

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
                url = reverse('Main:display_awareness',
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
            linkurl = reverse('Main:display_awareness',
                              kwargs={'campaignid': campaign.id, 'targetid': targetid})
            template = template.replace("FIXMEURL", linkurl)

        return render(request, "Main/awareness.html", {"template": template})

    return HttpResponseForbidden()


def target_autoclick(request, targetid):
    if target := AnonymousTarget.objects.filter(uniqueid=targetid):
        target = target.first()
        campaign = target.campaign_set.get()
        if campaign.status == "2" and not target.autoclick_time:
            target.autoclick_time = datetime.now(tz=get_current_timezone())
            target.save()

    return HttpResponse()


def target_openmail(request, targetid):
    if not Campaign.objects.filter(testid=targetid):
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


def target_reportmail(request, targetid):
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


def target_openattachment(request, targetid):
    if not Campaign.objects.filter(testid=targetid):
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


def internet_explorer_img_hack_template(template):
    soup = BeautifulSoup(template.text)

    for img in soup.findAll("img"):
        imgid = img["id"]
        img["src"] = reverse("getimage", args=[template.id, imgid], urlconf="Main.urls")

    return str(soup)


def internet_explorer_img_hack(request, templateid, imgid):
    template = get_object_or_404(Template, id=templateid)

    soup = BeautifulSoup(template.text, "html.parser")
    img = soup.find("img", {"id": imgid})

    if img is not None:
        tmp = img["src"].split(',')
        imgsrc = tmp[1]
        mime = tmp[0].split(';')[0].split(':')[1]
        return HttpResponse(b64decode(imgsrc), content_type=mime)

    return HttpResponseNotFound()
