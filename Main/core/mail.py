from base64 import b64decode
from email.header import Header
from email.mime.image import MIMEImage
from re import sub

from bs4 import BeautifulSoup
from django.conf import settings
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from Main.models import Campaign, AnonymousTarget


def build_email(campaign: Campaign):
    i = 0
    soup = BeautifulSoup(campaign.mail_template.text, "html.parser")
    imgs = []
    for img in soup.findAll("img"):
        if not img.has_attr("src") or not img["src"][:5].lower() == "data:":
            continue
        tmp = img["src"].split(',')
        if len(tmp) > 1:
            base64 = tmp[1]
            mime = tmp[0].split(';')[0].split(':')[1]
            mimeimg = MIMEImage(b64decode(base64))
            mimeimg.set_type(mime)
            mimeimg.add_header('Content-ID', '<img%s>' % i)
            imgs.append(mimeimg)
        img["src"] = "cid:img%s" % i
        if "style" in img:
            styles = img["style"].split(";")
            height = 0
            width = 0
            for style in styles:
                if "height" in style:
                    tmp = style.split(":")[1].replace("px", "")
                    height = str(int(tmp) * 75 / 100)
                if "width" in style:
                    tmp = style.split(":")[1].replace("px", "")
                    width = str(int(tmp) * 75 / 100)
            if height != 0:
                img["height"] = height
            if width != 0:
                img["width"] = width
        i += 1

    if campaign.enable_mail_tracker:
        if not soup.findAll("img", attrs={"src": "FIXMEMAILTRACKER"}):
            div = soup.new_tag('div', style='display: none')
            img = soup.new_tag("img", src="FIXMEMAILTRACKER", width=1, height=1)
            div.append(img)
            autoclick_link = soup.new_tag("a", href="FIXMEAUTOCLICKLINK")
            div.append(autoclick_link)
            soup.body.append(div)

    return {"text": str(soup), "imgs": imgs}


def build_attachment(campaign: Campaign):
    if campaign.campaign_type != "2":
        return ""
    i = 0
    soup = BeautifulSoup(campaign.attachment_template.text, "html.parser")
    imgs = []
    for img in soup.findAll("img"):
        if not img.has_attr("src") or not img["src"][:5].lower() == "data:":
            continue
        tmp = img["src"].split(',')
        mime = tmp[0].split(';')[0].split(':')[1]
        mimeimg = tmp[1]
        imgs.append((mimeimg, mime, "files/img%s" % i))
        img["src"] = "files/img%s" % i
        if "style" in img:
            styles = img["style"].split(";")
            height = 0
            width = 0
            for style in styles:
                if "height" in style:
                    tmp = style.split(":")[1].replace("px", "")
                    height = str(int(tmp) * 75 / 100)
                if "width" in style:
                    tmp = style.split(":")[1].replace("px", "")
                    width = str(int(tmp) * 75 / 100)
            if height != 0:
                img["height"] = height
            if width != 0:
                img["width"] = width
        i += 1

    if campaign.enable_attachment_tracker:
        if not soup.findAll("img", attrs={"src": "FIXMEDOCTRACKER"}):
            img = soup.new_tag("img", src="FIXMEDOCTRACKER")
            soup.body.append(img)

    if not soup.findAll("meta", attrs={"charset": "UTF-8"}):
        charset = soup.new_tag("meta", charset="UTF-8")
        soup.head.append(charset)

    result = ""
    result += "MIME-Version: 1.0\n"
    result += 'Content-Type: multipart/related; boundary="----=_Attachment_000_001"\n\n'
    result += "------=_Attachment_000_001\n"
    result += "Content-Location: file:///C:/document.html\n"
    result += 'Content-Type: text/html; charset="utf-8"\n\n'
    result += "%s\n\n\n" % soup
    for img in imgs:
        result += "------=_Attachment_000_001\n"
        result += "Content-Location: file:///C:/%s\n" % img[2]
        result += "Content-Type: %s\n" % img[1]
        result += "Content-Transfer-Encoding: base64\n\n"
        result += img[0]
        result += "\n\n\n"
    result += "------=_Attachment_000_001--\n"

    return result


def send_email(campaign: Campaign, recipient, targetid, con, mail_content):
    base_mail = mail_content
    mail_content = "Read this mail with a HTML compatible client"
    sender = campaign.from_name + '@' + campaign.from_domain.domain
    try:
        target = AnonymousTarget.objects.get(uniqueid=targetid)
    except ObjectDoesNotExist:
        target = None
    if campaign.display_name != "":
        from_mail = "%s <%s>" % (campaign.display_name, sender)
    else:
        from_mail = sender

    email = mail.EmailMultiAlternatives(campaign.mail_template.title, mail_content, from_mail, [recipient],
                                        connection=con)

    if campaign.host_subdomain is not None and campaign.host_subdomain != "":
        linkurl = "%s.%s%s" % (campaign.host_subdomain,
                               campaign.host_domain.domain,
                               reverse('Main:target_click',
                                       kwargs={'targetid': targetid})
                               )
    else:
        linkurl = '%s%s' % (campaign.host_domain.domain, reverse('Main:target_click', kwargs={'targetid': targetid}))
    imgurl = 'http://%s%s' % (
        campaign.host_domain.domain, reverse('Main:target_openmail', kwargs={'targetid': targetid}))

    html_content = base_mail["text"].replace("FIXMEURL", linkurl)

    if campaign.enable_mail_tracker:
        html_content = html_content.replace("FIXMEMAILTRACKER", imgurl)

    # add autoclick url
    if campaign.campaign_type in '134' and campaign.host_domain:
        autolink = f'http://{campaign.host_domain.domain}{reverse("Main:target_autoclick", kwargs={"targetid": targetid})}'
        html_content = html_content.replace("FIXMEAUTOCLICKLINK", autolink)

    if target:
        for att in target.attributes.all():
            att.key = sub(r'ORDN-[0-9]{3}-', '', att.key)
            html_content = html_content.replace(f'(${att.key}$)', att.value)

    email.attach_alternative(html_content, "text/html")
    email.mixed_subtype = 'related'
    for img in base_mail["imgs"]:
        email.attach(img)

    email.extra_headers = {settings.PHISHING_MAIL_HEADER: "[%s]" % targetid}
    email.send(fail_silently=False)


def send_email_with_attachment(campaign: Campaign, recipient, targetid, con, mail_content, attachment_content):
    base_mail = mail_content
    attachment_content = attachment_content
    try:
        target = AnonymousTarget.objects.get(uniqueid=targetid)
    except ObjectDoesNotExist:
        target = None
    mail_content = "Read this mail with a HTML compatible client"
    sender = campaign.from_name + '@' + campaign.from_domain.domain
    if campaign.display_name != "":
        from_mail = "%s <%s>" % (campaign.display_name, sender)
    else:
        from_mail = sender

    email = mail.EmailMultiAlternatives(campaign.mail_template.title, mail_content, from_mail, [recipient],
                                        connection=con)

    imgurl_mail = "http://%s%s" % (
        campaign.from_domain.domain, reverse('Main:target_openmail', kwargs={'targetid': targetid}))
    imgurl_attachment = "http://%s%s" % (
        campaign.from_domain.domain, reverse('Main:target_openattachment', kwargs={'targetid': targetid}))

    html_content = base_mail["text"]
    mhtml_attach = attachment_content
    if campaign.enable_mail_tracker:
        html_content = html_content.replace("FIXMEMAILTRACKER", imgurl_mail)
    if campaign.enable_attachment_tracker:
        mhtml_attach = mhtml_attach.replace("FIXMEDOCTRACKER", imgurl_attachment)

    if target:
        for att in target.attributes.all():
            att.key = sub(r'ORDN-[0-9]{3}-', '', att.key)
            html_content = html_content.replace(f'(${att.key}$)', att.value)
    email.attach_alternative(html_content, 'text/html')
    temp = f'{campaign.attachment_template.title}.doc'
    filename = Header(temp, 'utf-8').encode()
    email.attach(filename=filename,
                 content=mhtml_attach.encode("utf-8"),
                 mimetype="application/msword")
    email.mixed_subtype = 'related'
    for img in base_mail["imgs"]:
        email.attach(img)
    email.extra_headers = {settings.PHISHING_MAIL_HEADER: "[%s]" % targetid}
    email.send(fail_silently=False)
