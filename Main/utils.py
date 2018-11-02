from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_mail(recipients, template, subject):
    from_email = settings.SERVER_EMAIL
    msg = EmailMultiAlternatives(subject, template, from_email, recipients)
    msg.attach_alternative(template, "text/html")
    msg.send()


def send_alert_new_campaign(size, organizer, campaign_subject, sender):
    subject = "/!\\ Swordphish Campaign has just started /!\\"
    template = '''<p><b><font color="red">A new swordphish campain has just started</font></b></p>
                <p>The campaign is organized by: <strong>%s</strong><p>
                <p>The campaign will target <strong>%s people</strong><p>
                <p>The mail subject is: <strong>%s</strong><p>
                <p>The mail sender is: <strong>%s</strong><p>''' % (organizer,
                                                                    size,
                                                                    campaign_subject,
                                                                    sender
                                                                    )
    recipients = settings.ALERT_RECIPIENTS
    send_mail(recipients, template, subject)
