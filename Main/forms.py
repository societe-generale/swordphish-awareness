import re

from bs4 import BeautifulSoup, Doctype
from bootstrap3_datetime.widgets import DateTimePicker
from django.forms import ModelForm, EmailField, ValidationError
from django.forms import CharField, Textarea, CheckboxSelectMultiple
from django.core.validators import URLValidator
from django.utils.translation import gettext as _
from django.conf import settings
from django.db.models import Q

from Main.models import TargetList, Target, Campaign, Attribute, Template


class TargetsListForm(ModelForm):

    class Meta:
        model = TargetList
        fields = ['name']


class NewTargetForm(ModelForm):

    class Meta:
        model = Target
        fields = ['mail_address']


class AttributeForm(ModelForm):

    class Meta:
        model = Attribute
        fields = ['key', 'value']

    def clean(self):
        return


class SimpleMailForm(ModelForm):

    def clean_text(self):
        text = self.cleaned_data["text"]

        soup = BeautifulSoup(text, "html.parser")
        if not isinstance(soup.contents[0], Doctype):
            doctype = Doctype("html")
            soup.insert(0, doctype)

        return str(soup)

    def clean(self):
        cleaned_data = super(SimpleMailForm, self).clean()

        if "FIXMEURL" not in cleaned_data.get("text"):
            self.add_error("text", "The mail content must include a link pointing to FIXMEURL")

    def save(self, commit=True):
        m = super(SimpleMailForm, self).save(commit=False)

        m.template_type = "1"

        if commit:
            m.save()

        return m

    class Meta:
        model = Template
        fields = ['name', 'title', 'text', 'public']
        labels = {
            'name': _('Template name'),
            'title': _('Subject'),
            'public': _('Share this template with everyone'),
        }


class MailWithAttachmentForm(ModelForm):

    def clean_text(self):
        text = self.cleaned_data["text"]

        soup = BeautifulSoup(text, "html.parser")
        if not isinstance(soup.contents[0], Doctype):
            doctype = Doctype("html")
            soup.insert(0, doctype)

        return str(soup)

    def save(self, commit=True):
        m = super(MailWithAttachmentForm, self).save(commit=False)

        soup = BeautifulSoup(m.text, "html.parser")
        if not isinstance(soup.contents[0], Doctype):
            doctype = Doctype("html")
            soup.insert(0, doctype)

        m.text = str(soup)

        m.template_type = "2"

        if commit:
            m.save()

        return m

    class Meta:
        model = Template
        fields = ['name', 'title', 'text', 'public']
        labels = {
            'name': _('Template name'),
            'public': _('Share this template with everyone'),
            'title': _('Subject')}


class AttachmentForm(ModelForm):

    def clean_text(self):
        text = self.cleaned_data["text"]

        soup = BeautifulSoup(text, "html.parser")
        if not isinstance(soup.contents[0], Doctype):
            doctype = Doctype("html")
            soup.insert(0, doctype)

        return str(soup)

    def save(self, commit=True):
        m = super(AttachmentForm, self).save(commit=False)

        soup = BeautifulSoup(m.text, "html.parser")
        if not isinstance(soup.contents[0], Doctype):
            doctype = Doctype("html")
            soup.insert(0, doctype)

        m.text = str(soup)

        m.template_type = "3"

        if commit:
            m.save()

        return m

    class Meta:
        model = Template
        fields = ['name', 'title', 'text', 'public']
        labels = {
            'name': _('Template name'),
            'public': _('Share this template with everyone'),
            'title': _('Filename')
        }


class Redirection(ModelForm):

    def clean_title(self):
        data = self.cleaned_data['title']
        validator = URLValidator()
        validator(data)
        return data

    def save(self, commit=True):
        m = super(Redirection, self).save(commit=False)

        m.template_type = "4"

        if commit:
            m.save()

        return m

    class Meta:
        model = Template
        fields = ['name', 'title', 'public']
        labels = {
            'name': _('Template name'),
            'public': _('Share this template with everyone'),
            'title': _('URL')
        }


class Awareness(ModelForm):

    def clean_text(self):
        text = self.cleaned_data["text"]

        soup = BeautifulSoup(text, "html.parser")
        if not isinstance(soup.contents[0], Doctype):
            doctype = Doctype("html")
            soup.insert(0, doctype)

        imgid = 0
        for img in soup.findAll("img"):
            img["id"] = "img%s" % imgid
            imgid += 1

        return str(soup)

    def clean_title(self):
        return ""

    def save(self, commit=True):
        m = super(Awareness, self).save(commit=False)

        m.template_type = "5"

        if commit:
            m.save()

        return m

    class Meta:
        model = Template
        fields = ['name', 'text', 'public']
        labels = {
            'name': _('Template name'),
            'public': _('Share this template with everyone'),
            'text': _('Text')
        }


class CredsHarvesterForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(CredsHarvesterForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.config_name = 'withforms'
        self.fields['text'].widget.config = settings.CKEDITOR_CONFIGS["withforms"]

    def clean_text(self):
        text = self.cleaned_data["text"]

        soup = BeautifulSoup(text, "html.parser")
        if not isinstance(soup.contents[0], Doctype):
            doctype = Doctype("html")
            soup.insert(0, doctype)

        forms = soup.findAll("form")
        if not forms or len(forms) > 1:
            raise ValidationError(_("The template must contain one form"))

        if not forms[0].findAll("input", attrs={"type": "submit"}):
            raise ValidationError(_("The form must have a submit button"))

        imgid = 0
        for img in soup.findAll("img"):
            img["id"] = "img%s" % imgid
            imgid += 1

        return str(soup)

    def clean_title(self):
        return ""

    def save(self, commit=True):
        m = super(CredsHarvesterForm, self).save(commit=False)

        m.template_type = "6"

        if commit:
            m.save()

        return m

    class Meta:
        model = Template
        fields = ['name', 'text', 'public']
        labels = {
            'name': _('Template name'),
            'public': _('Share this template with everyone'),
            'text': _('Text')
        }


class FakeRansomForm(ModelForm):

    def clean_text(self):
        text = self.cleaned_data["text"]
        timeout = self.data["timeout"]

        javascript = """
        function fullscreen_display() {
                var images = document.getElementsByTagName('img');
                for (i = 0; i < images.length;i++ ) {
                    images[i].style.display = "none";
                }
                var divs = document.getElementsByTagName('div');
                for (i = 0; i < divs.length;i++ ) {
                    var images = divs[i].getElementsByTagName('img');
                    for (j = 0; j < images.length;j++ ) {
                        images[j].style.display = "block";
                        images[j].style.marginLeft = "auto";
                        images[j].style.marginRight = "auto";
                    }
                    divs[i].style.display = "block";
                }
            }
        function launchIntoFullscreen(element) {
                if(element.requestFullscreen) {
                    element.requestFullscreen();
                }
                else if(element.mozRequestFullScreen) {
                    element.mozRequestFullScreen();
                } else if(element.webkitRequestFullscreen) {
                    element.webkitRequestFullscreen();
                } else if(element.msRequestFullscreen) {
                    element.msRequestFullscreen();
                }
                    fullscreen_display();
                    window.setTimeout(function() {
                    location.href = "FIXMEURL";
                }, %s);
        }
    """ % (int(timeout) * 1000)

        soup = BeautifulSoup(text, "html.parser")
        if not isinstance(soup.contents[0], Doctype):
            doctype = Doctype("html")
            soup.insert(0, doctype)

        if "style" in soup.body.attrs:
            soup.html.attrs["style"] = soup.body.attrs["style"]

        script = soup.new_tag("script")
        script.attrs["type"] = "text/javascript"
        script.append(javascript)

        jquery = soup.new_tag("script")
        jquery.attrs["type"] = "text/javascript"
        jquery.attrs["src"] = "https://code.jquery.com/jquery.min.js"

        jqlist = soup.head.findAll("script", {"src": "https://code.jquery.com/jquery.min.js"})
        if not jqlist:
            soup.head.append(jquery)

        for div in soup.body.findAll("div"):
            if "style" in div.attrs:
                div.attrs["style"] = "%s; %s;" % (div.attrs["style"], "display:none")
            else:
                div.attrs["style"] = "display:none"

        scriptlist = soup.head.findAll("script", string="launchIntoFullscreen")
        if not scriptlist:
            soup.head.append(script)

        if not soup.body.findAll("img"):
            raise ValidationError(_("The form must have at least one image"))

        imgid = 0
        for img in soup.findAll("img"):
            img["onclick"] = "javascript:launchIntoFullscreen(document.documentElement);"
            img["id"] = "img%s" % imgid
            imgid += 1

        return str(soup)

    def clean_title(self):
        return ""

    def save(self, commit=True):
        m = super(FakeRansomForm, self).save(commit=False)

        m.template_type = "7"

        if commit:
            m.save()

        return m

    class Meta:
        model = Template
        fields = ['name', 'text', 'timeout', 'public']
        labels = {
            'name': _('Template name'),
            'public': _('Share this template with everyone'),
            'timeout': _('Time to wait (in seconds) before redirection'),
            'text': _('Text')
        }


class TestCampaignForm(ModelForm):
    recipient = EmailField(label=_("Recipient"))

    def __init__(self, *args, **kwargs):
        super(TestCampaignForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs['readonly'] = 'readonly'

    class Meta:
        model = Campaign
        fields = ['name']


class CampaignForm(ModelForm):
    visible_users = None

    def __init__(self, user, *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)
        self.visible_users = user.swordphishuser.visible_users()
        self.fields["targets"].queryset = self.get_targets_list(user)

    def get_targets_list(self, user):
        visible_users = user.swordphishuser.visible_users()
        targetslists = TargetList.objects.filter(author__in=visible_users)
        return targetslists

    def clean(self):
        cleaned_data = super(CampaignForm, self).clean()
        sdate = cleaned_data.get("start_date")
        edate = cleaned_data.get("end_date")

        if sdate > edate:
            self.add_error('start_date', "Start date cannot be after end date")
            self.add_error('end_date', "End date cannot be before start date")

        if sdate == edate:
            self.add_error('start_date', "Start date cannot be the same than the end date")
            self.add_error('end_date', "End date cannot the same than the start date")

    class Meta:
        model = Campaign
        fields = [
                    'name',
                    'targets',
                    'start_date',
                    'end_date',
                    'from_name',
                    'from_domain',
                    'display_name'
                 ]
        widgets = {
            'start_date': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm"}),
            'end_date': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm"}),
            'targets': CheckboxSelectMultiple()}
        labels = {
            'from_name': _('On behalf of'),
            'from_domain': _('Domain'),
            'display_name': _('Display Name')}


class StandardCampaignForm(CampaignForm):

    def __init__(self, user, *args, **kwargs):
        super(StandardCampaignForm, self).__init__(user, *args, **kwargs)
        self.fields['onclick_action'].required = True
        self.fields['onclick_action'].widget.attrs.update({'required': 'required'})
        mail_templates = Template.objects.filter(Q(template_type="1") & (
                                                 Q(author__in=self.visible_users) | Q(public=True)
                                                 ))
        self.fields['mail_template'].queryset = mail_templates
        onclick_action = Template.objects.filter(Q(template_type__in=["4", "5"]) & (
                                                 Q(author__in=self.visible_users) | Q(public=True)
                                                 ))
        self.fields['onclick_action'].queryset = onclick_action

    def clean_host_domain(self):
        host_domain = self.cleaned_data["host_domain"]

        if not host_domain:
            raise ValidationError(_("Please specify a host domain"))

        return host_domain

    def clean_onclick_action(self):
        templates = Template.objects.filter(Q(template_type__in=["4", "5"]) & (
                                            Q(author__in=self.visible_users) | Q(public=True)
                                            ))
        template = self.cleaned_data["onclick_action"]
        if template not in templates:
            raise ValidationError(_("You are not allowed to use this template"))
        else:
            return template

    def clean_mail_template(self):
        templates = Template.objects.filter(Q(template_type="1") & (
                                            Q(author__in=self.visible_users) | Q(public=True)
                                            ))
        template = self.cleaned_data["mail_template"]
        if template not in templates:
            raise ValidationError(_("You are not allowed to use this template"))
        else:
            return template

    def save(self, commit=True):
        m = super(StandardCampaignForm, self).save(commit=False)

        m.campaign_type = "1"

        if commit:
            m.save()

        return m

    class Meta(CampaignForm.Meta):
        fields = CampaignForm.Meta.fields + [
                                                "mail_template",
                                                "enable_mail_tracker",
                                                "onclick_action",
                                                "host_subdomain",
                                                "host_domain"
                                            ]

        CampaignForm.Meta.labels.update({'onclick_action': _('Action after click')})


class AttachmentCampaignForm(CampaignForm):

    def __init__(self, user, *args, **kwargs):
        super(AttachmentCampaignForm, self).__init__(user, *args, **kwargs)
        self.fields['attachment_template'].required = True
        self.fields['attachment_template'].widget.attrs.update({'required': 'required'})

        mail_template = Template.objects.filter(Q(template_type="2") & (
                                                Q(author__in=self.visible_users) | Q(public=True)
                                                ))

        self.fields['mail_template'].queryset = mail_template

        atch_template = Template.objects.filter(Q(template_type="3") & (
                                                Q(author__in=self.visible_users) | Q(public=True)
                                                ))

        self.fields['attachment_template'].queryset = atch_template

    def save(self, commit=True):
        m = super(AttachmentCampaignForm, self).save(commit=False)

        m.campaign_type = "2"

        if commit:
            m.save()

        return m

    def clean_mail_template(self):
        templates = Template.objects.filter(Q(template_type="2") & (
                                            Q(author__in=self.visible_users) | Q(public=True)
                                            ))
        template = self.cleaned_data["mail_template"]
        if template not in templates:
            raise ValidationError(_("You are not allowed to use this template"))
        else:
            return template

    def clean_attachment_template(self):
        templates = Template.objects.filter(Q(template_type="3") & (
                                            Q(author__in=self.visible_users) | Q(public=True)
                                            ))
        template = self.cleaned_data["attachment_template"]
        if template not in templates:
            raise ValidationError(_("You are not allowed to use this template"))
        else:
            return template

    class Meta(CampaignForm.Meta):
        fields = CampaignForm.Meta.fields + [
                                                "mail_template",
                                                "enable_mail_tracker",
                                                "attachment_template",
                                                "enable_attachment_tracker"
                                            ]


class FakeFormCampaignForm(CampaignForm):

    def __init__(self, user, *args, **kwargs):
        super(FakeFormCampaignForm, self).__init__(user, *args, **kwargs)
        mail_template = Template.objects.filter(Q(template_type="1") & (
                                                Q(author__in=self.visible_users) | Q(public=True)
                                                ))
        self.fields['mail_template'].queryset = mail_template
        fake_form = Template.objects.filter(Q(template_type="6") & (
                                            Q(author__in=self.visible_users) | Q(public=True)))
        self.fields['fake_form'].queryset = fake_form
        self.fields['fake_form'].required = True
        self.fields['fake_form'].widget.attrs.update({'required': 'required'})
        self.fields['onclick_action'].required = True
        self.fields['onclick_action'].widget.attrs.update({'required': 'required'})
        onclick_action = Template.objects.filter(Q(template_type__in=["4", "5"]) & (
                                                 Q(author__in=self.visible_users) | Q(public=True)
                                                 ))
        self.fields['onclick_action'].queryset = onclick_action

    def clean_host_domain(self):
        host_domain = self.cleaned_data["host_domain"]

        if not host_domain:
            raise ValidationError(_("Please specify a host domain"))

        return host_domain

    def clean_onclick_action(self):
        templates = Template.objects.filter(Q(template_type__in=["4", "5"]) & (
                                            Q(author__in=self.visible_users) | Q(public=True)
                                            ))
        template = self.cleaned_data["onclick_action"]
        if template not in templates:
            raise ValidationError(_("You are not allowed to use this template"))
        else:
            return template

    def clean_mail_template(self):
        templates = Template.objects.filter(Q(template_type="1") & (
                                            Q(author__in=self.visible_users) | Q(public=True)
                                            ))
        template = self.cleaned_data["mail_template"]
        if template not in templates:
            raise ValidationError(_("You are not allowed to use this template"))
        else:
            return template

    def clean_fake_form(self):
        templates = Template.objects.filter(Q(template_type="6") & (
                                            Q(author__in=self.visible_users) | Q(public=True)
                                            ))
        template = self.cleaned_data["fake_form"]
        if template not in templates:
            raise ValidationError(_("You are not allowed to use this template"))
        else:
            return template

    def save(self, commit=True):
        m = super(FakeFormCampaignForm, self).save(commit=False)

        m.campaign_type = "3"

        if commit:
            m.save()

        return m

    class Meta(CampaignForm.Meta):
        fields = CampaignForm.Meta.fields + [
                                                "mail_template",
                                                "enable_mail_tracker",
                                                "fake_form",
                                                "onclick_action",
                                                "host_subdomain", "host_domain"
                                            ]
        CampaignForm.Meta.labels.update({
            'onclick_action': _('Action after submit'),
            'fake_form': _('Fake form to display')})


class FakeRansomCampaignForm(CampaignForm):

    def __init__(self, user, *args, **kwargs):
        super(FakeRansomCampaignForm, self).__init__(user, *args, **kwargs)
        mail_template = Template.objects.filter(Q(template_type="1") & (
                                                Q(author__in=self.visible_users) | Q(public=True)
                                                ))

        fake_ransom = Template.objects.filter(Q(template_type="7") & (
                                              Q(author__in=self.visible_users) | Q(public=True)
                                              ))

        onclick_action = Template.objects.filter(Q(template_type__in=["4", "5"]) & (
                                                 Q(author__in=self.visible_users) | Q(public=True)
                                                 ))

        self.fields['mail_template'].queryset = mail_template
        self.fields['fake_ransom'].queryset = fake_ransom
        self.fields['fake_ransom'].required = True
        self.fields['fake_ransom'].widget.attrs.update({'required': 'required'})
        self.fields['onclick_action'].required = True
        self.fields['onclick_action'].widget.attrs.update({'required': 'required'})
        self.fields['onclick_action'].queryset = onclick_action

    def clean_host_domain(self):
        host_domain = self.cleaned_data["host_domain"]

        if not host_domain:
            raise ValidationError(_("Please specify a host domain"))

        return host_domain

    def clean_onclick_action(self):
        templates = Template.objects.filter(Q(template_type__in=["4", "5"]) & (
                                            Q(author__in=self.visible_users) | Q(public=True)
                                            ))
        template = self.cleaned_data["onclick_action"]
        if template not in templates:
            raise ValidationError(_("You are not allowed to use this template"))
        else:
            return template

    def clean_mail_template(self):
        templates = Template.objects.filter(Q(template_type="1") & (
                                            Q(author__in=self.visible_users) | Q(public=True)
                                            ))
        template = self.cleaned_data["mail_template"]
        if template not in templates:
            raise ValidationError(_("You are not allowed to use this template"))
        else:
            return template

    def clean_fake_ransom(self):
        templates = Template.objects.filter(Q(template_type="7") & (
                                            Q(author__in=self.visible_users) | Q(public=True)
                                            ))
        template = self.cleaned_data["fake_ransom"]
        if template not in templates:
            raise ValidationError(_("You are not allowed to use this template"))
        else:
            return template

    def save(self, commit=True):
        m = super(FakeRansomCampaignForm, self).save(commit=False)

        m.campaign_type = "4"

        if commit:
            m.save()

        return m

    class Meta(CampaignForm.Meta):
        fields = CampaignForm.Meta.fields + [
                                                "mail_template",
                                                "enable_mail_tracker",
                                                "fake_ransom",
                                                "onclick_action",
                                                "host_subdomain",
                                                "host_domain"
                                            ]
        CampaignForm.Meta.labels.update({
            'onclick_action': _('Action after redirect'),
            'fake_ransom': _('Fake ransom to display')})


class ReportForm(ModelForm):
    ids = CharField(widget=Textarea, required=True, label=_("IDs or URLs"))

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs['readonly'] = 'readonly'

    def clean_ids(self):
        ids = self.cleaned_data["ids"]
        regex = r'[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}'
        a = re.findall(regex, ids)
        if not a:
            raise ValidationError(_("Please specify at least one id..."))
        else:
            return ids

    class Meta:
        fields = ['name']
        model = Campaign
