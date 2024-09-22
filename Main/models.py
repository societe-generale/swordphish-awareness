from datetime import datetime
from uuid import uuid4

from ckeditor.fields import RichTextField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db.models import PositiveIntegerField, CharField, EmailField, IntegerField, DateTimeField, BooleanField
from django.db.models import Q, Model, PROTECT, SET, ForeignKey, ManyToManyField
from django.utils.translation import gettext as _

from LocalUsers.models import SwordphishUser, get_admin


class Attribute(Model):
    key = CharField(db_index=True, max_length=240)
    value = CharField(db_index=True, max_length=240)

    def __str__(self):
        return f'{self.key} => {self.value}'

    class Meta:
        unique_together = ('key', 'value')


class Target(Model):
    mail_address = EmailField(db_index=True, )
    attributes = ManyToManyField(Attribute)

    def __str__(self):
        return self.mail_address

    def add_attribute(self, attribute, value):
        if not self.attributes.filter(key=attribute, value=value):
            try:
                new_att = Attribute.objects.get(key=attribute, value=value)
            except ObjectDoesNotExist:
                new_att = Attribute.objects.create(key=attribute, value=value)
            self.attributes.add(new_att)
            self.save()


class TargetList(Model):
    class Meta:
        ordering = ["name", "-creation_date"]

    name = CharField(max_length=240)
    targets = ManyToManyField(Target)
    author = ForeignKey(SwordphishUser, null=True, on_delete=SET(get_admin))
    creation_date = DateTimeField(blank=True, default=datetime.now)

    def __str__(self):
        return self.name

    def remove_target(self, target):
        self.targets.remove(target)
        self.targets.filter(mail_address=target.mail_address).delete()

    def is_used(self):
        return Campaign.objects.filter(targets=self).count()


class AnonymousTarget(Model):
    uniqueid = CharField(db_index=True, max_length=36, default=uuid4)
    attributes = ManyToManyField(Attribute)
    mail_sent_time = DateTimeField(blank=True, null=True)
    mail_opened = BooleanField(default=False)
    mail_opened_time = DateTimeField(blank=True, null=True)
    link_clicked = BooleanField(default=False)
    link_clicked_time = DateTimeField(blank=True, null=True)
    autoclick_time = DateTimeField(default=None, null=True)
    attachment_opened = BooleanField(default=False)
    attachment_opened_time = DateTimeField(blank=True, null=True)
    form_submitted = BooleanField(default=False)
    form_submitted_time = DateTimeField(blank=True, null=True)
    reported = BooleanField(default=False)
    reported_time = DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.uniqueid

    def import_attributes(self, target):
        for att in target.attributes.all():
            self.attributes.add(att)


class PhishmailDomain(Model):
    class Meta:
        ordering = ["domain"]

    domain = CharField(max_length=50)
    enabled = BooleanField(default=True, help_text=_('Enable domain'))

    def __str__(self):
        return self.domain


class Template(Model):
    class Meta:
        ordering = ["name", "-creation_date"]

    TEMPLATE_TYPE = [
        ('#1', _('Mail with link')),
        ('1', _('Mail with link template')),
        ('#2', _('Mail with attachment')),
        ('2', _('Mail with attachment template')),
        ('3', _('Attachment template')),
        ('#3', _('Action after click')),
        ('4', _('Redirection')),
        ('5', _('Awareness template')),
        ('6', _('Fake form template')),
        ('7', _('Fake ransomware template')),
    ]

    template_type = CharField(max_length=2, choices=TEMPLATE_TYPE, default=1)
    name = CharField(max_length=200)
    author = ForeignKey(SwordphishUser, on_delete=SET(get_admin))
    creation_date = DateTimeField(auto_now_add=True, blank=True)
    public = BooleanField(default=False)
    title = CharField(max_length=100)
    timeout = PositiveIntegerField(default=10)
    text = RichTextField()

    def __str__(self):
        return self.name

    def is_used(self):
        return Campaign.objects.filter(Q(mail_template=self) | Q(attachment_template=self) | Q(onclick_action=self) |
                                       Q(fake_form=self) | Q(fake_ransom=self)).count()


class Campaign(Model):
    class Meta:
        ordering = ["-start_date", "-end_date", "creation_date"]

    CAMPAIGN_TYPES = [
        ("1", _("Simple")),
        ("2", _("With Attachment")),
        ("3", _("Fake Form")),
        ("4", _("Fake Ransomware"))
    ]

    CAMPAIGN_STATUS = [
        ('1', _("Not Started")),
        ('2', _("Running")),
        ('3', _("Finished")),
    ]

    campaign_type = CharField(max_length=1, choices=CAMPAIGN_TYPES, default="1")
    name = CharField(max_length=200)
    author = ForeignKey(SwordphishUser, on_delete=SET(get_admin))
    creation_date = DateTimeField(auto_now_add=True, blank=True)
    start_date = DateTimeField()
    end_date = DateTimeField()
    targets = ManyToManyField(TargetList)
    targets_count = IntegerField(default=0)
    anonymous_targets = ManyToManyField(AnonymousTarget)
    status = CharField(max_length=1, choices=CAMPAIGN_STATUS, default="1")
    mail_template = ForeignKey(Template, related_name='%(class)s_mail', on_delete=PROTECT)
    from_name = CharField(max_length=50)
    from_domain = ForeignKey(PhishmailDomain, related_name='%(class)s_from_domain', on_delete=PROTECT)
    displayname_regex = RegexValidator(regex=r'^[^@]{1,100}$', message=_("Display name must not contains @"))
    display_name = CharField(validators=[displayname_regex], max_length=100, null=True, blank="True")
    attachment_template = ForeignKey(Template, default=None, blank=True, null=True,
                                     related_name='%(class)s_attachment', on_delete=PROTECT)
    fake_form = ForeignKey(Template, default=None, blank=True, null=True, related_name='%(class)s_fake_form',
                           on_delete=PROTECT)
    fake_ransom = ForeignKey(Template, default=None, blank=True, null=True, related_name='%(class)s_fake_ransom',
                             on_delete=PROTECT)
    onclick_action = ForeignKey(Template, default=None, blank=True, null=True, related_name='%(class)s_action',
                                on_delete=PROTECT)
    host_subdomain_regex = RegexValidator(regex=r'^[-.a-z0-9]{0,200}(?<!\.)$',
                                          message=_("Only a-z, 0-9, - and ., must not end with a ."))
    host_subdomain = CharField(validators=[host_subdomain_regex], max_length=200, blank=True, null=True)
    host_domain = ForeignKey(PhishmailDomain, default=None, blank=True, null=True,
                             related_name='%(class)s_host_domain', on_delete=PROTECT)
    enable_mail_tracker = BooleanField(default=True)
    enable_attachment_tracker = BooleanField(default=True)
    testid = CharField(max_length=36, default=uuid4)

    def __str__(self):
        return self.name

    def count_targets(self):
        return sum([t.targets.count() for t in self.targets.all()])

    def links_clicked(self, ):
        return self.anonymous_targets.filter(link_clicked=True).count()

    def links_autoclicked(self):
        return self.anonymous_targets.filter(autoclick_time__isnull=False).count()

    def mails_reported(self):
        return self.anonymous_targets.filter(reported=True).count()

    def mails_open(self):
        return self.anonymous_targets.filter(mail_opened=True).count()

    def mails_sent(self):
        return self.anonymous_targets.count()

    def attachments_open(self):
        return self.anonymous_targets.filter(attachment_opened=True).count()

    def forms_submitted(self):
        return self.anonymous_targets.filter(form_submitted=True).count()
