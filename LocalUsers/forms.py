from django.forms import ModelForm, CharField, PasswordInput, ValidationError, ChoiceField
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from LocalUsers.models import SwordphishUser, Entity, Region


class SwordphishUserForm(ModelForm):
    class Meta:
        model = SwordphishUser
        fields = ['phone_number']


class UserForm(ModelForm):
    password = CharField(widget=PasswordInput(), required=False)
    password_confirmation = CharField(widget=PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_first_name(self):
        data = self.cleaned_data['first_name']
        if data == "":
            raise ValidationError(_("First name must be provided"))
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name']
        if data == "":
            raise ValidationError(_("First name must be provided"))
        return data

    def clean_password_confirmation(self):
        passw = self.cleaned_data['password']
        conf = self.cleaned_data['password_confirmation']

        if passw != conf:
            raise ValidationError(_("Password and confirmation are not equal"))
        return passw


class CreateUserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_first_name(self):
        data = self.cleaned_data['first_name'].capitalize()
        if data == "":
            raise ValidationError(_("First name must be provided"))
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name'].upper()
        if data == "":
            raise ValidationError(_("First name must be provided"))
        return data

    def clean_email(self):
        data = self.cleaned_data['email'].lower()
        if data == "":
            raise ValidationError(_("Email must be provided"))
        return data


class LostpasswordForm(ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        data = self.cleaned_data['email'].lower()
        if data == "":
            raise ValidationError(_("Email must be provided"))
        return data


class ChangePasswordForm(UserForm):
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields["password"].widget.attrs['required'] = True
        self.fields["password_confirmation"].widget.attrs['required'] = True
        self.fields["email"].widget.attrs['readonly'] = 'readonly'


class EditMyProfileForm(UserForm):
    old_password = CharField(widget=PasswordInput(), required=True)

    class Meta:
        model = User
        fields = [
                    'first_name',
                    'last_name',
                    'email',
                    'old_password',
                    'password',
                    'password_confirmation'
                 ]

    def __init__(self, *args, **kwargs):
        super(EditMyProfileForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget.attrs['readonly'] = 'readonly'

    def clean_old_password(self):
        if self.instance.check_password(self.cleaned_data["old_password"]):
            return self.cleaned_data['old_password']
        raise ValidationError(_("The current password is not correct"))


class EntityForm(ModelForm):
    class Meta:
        model = Entity
        fields = ['name']


class AddAdminForm(ModelForm):
    users = ChoiceField()

    def __init__(self, *args, **kwargs):
        super(AddAdminForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs['readonly'] = 'readonly'
        self.fields["users"].choices = self.get_admin_list()

    def get_admin_list(self):
        result = []
        swordphishusers = SwordphishUser.objects.all()
        instanceadmins = self.instance.admins.all()
        for user in swordphishusers:
            if user not in instanceadmins:
                result.append((user.id, "%s %s (%s)" % (user.user.last_name,
                                                        user.user.first_name,
                                                        user.user.email)
                               ))
        return result

    def clean_users(self):
        user = self.cleaned_data['users']
        if user == "":
            raise ValidationError(_("User must be provided"))

        testuser = SwordphishUser.objects.get(pk=user)

        if testuser is None:
            raise ValidationError(_("This user doesn't exist"))

        instanceadmins = self.instance.admins.all()
        for users in instanceadmins:
            if users.id == user:
                raise ValidationError(_("User is already admin for this entity"))

        return user

    class Meta:
        model = Entity
        fields = ["name"]


class RegionForm(ModelForm):
    entity = ChoiceField()

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(RegionForm, self).__init__(*args, **kwargs)
        self.fields["entity"].choices = self.get_entities_list(current_user)

    def get_entities_list(self, current_user):
        result = []
        if current_user.is_staff:
            entities = Entity.objects.all()
        else:
            entities = current_user.swordphishuser.entities()
        for entity in entities:
            result.append((entity.id, "%s" % (entity.name)))
        return result

    def clean_entity(self):
        entity = self.cleaned_data['entity']
        if entity == "":
            raise ValidationError(_("Entity must be provided"))

        testentity = Entity.objects.get(pk=entity)

        if testentity is None:
            raise ValidationError(_("This entity doesn't exist"))

        return entity

    class Meta:
        model = Region
        fields = ['name']


class AddUserInRegionForm(ModelForm):
    users = ChoiceField()

    def __init__(self, *args, **kwargs):
        super(AddUserInRegionForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs['readonly'] = 'readonly'
        self.fields["users"].choices = self.get_users_list()

    def get_users_list(self):
        result = []
        swordphishusers = SwordphishUser.objects.all()
        for user in swordphishusers:
            result.append((user.id, "%s %s (%s)" % (user.user.last_name,
                                                    user.user.first_name,
                                                    user.user.email)
                           ))
        return result

    def clean_users(self):
        user = self.cleaned_data['users']
        if user == "":
            raise ValidationError(_("User must be provided"))

        testuser = SwordphishUser.objects.get(pk=user)

        if testuser is None:
            raise ValidationError(_("This user doesn't exist"))

        instancemembers = self.instance.members.all()
        for users in instancemembers:
            if users.id == user:
                raise ValidationError(_("User is already in this region"))

        instanceadmins = self.instance.entity.admins.all()
        for users in instanceadmins:
            if users.id == user:
                raise ValidationError(_("User is admin of the related entity"))

        return user

    class Meta:
        model = Region
        fields = ["name"]
