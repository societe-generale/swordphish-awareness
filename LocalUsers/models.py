from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.core.validators import RegexValidator

# Create your models here.



class SwordphishUser(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message=_("Expected phone number format: '+999999999'")
                                 )
    phone_number = models.CharField(validators=[phone_regex], blank=True, max_length=20)
    must_change_password = models.BooleanField(default=False)

    def __str__(self):
        return "%s %s (%s)" % (self.user.first_name, self.user.last_name, self.user.email)

    def subordinates(self, mail=None):
        users_list = []
        if self.user.is_staff:
            if mail is None:
                users_list.extend(SwordphishUser.objects.all())
            else:
                users_list.extend(SwordphishUser.objects.filter(user__email__icontains=mail))
        elif self.entity_set.count:
            entities = self.entity_set.all()
            for entity in entities:
                for region in entity.region_set.all():
                    if mail is None:
                        users_list.extend(region.members.all())
                    else:
                        users_list.extend(region.members.filter(user__email__icontains=mail))
        return users_list

    def entities(self):
        entities_list = []
        if self.user.is_staff:
            entities_list.extend(Entity.objects.all())
        elif self.entity_set.count:
            entities_list = self.entity_set.all()
        return entities_list

    def regions(self):
        regions_list = []
        if self.user.is_staff:
            regions_list.extend(Region.objects.all())
        else:
            ents = self.entities()
            for entity in ents:
                regions_list.extend(Region.objects.filter(entity=entity))
            membership = RegionMembership.objects.filter(user=self)
            for region in membership:
                regions_list.append(region.region)

        return regions_list

    def visible_users(self):
        users_list = []
        if self.user.is_staff:
            users_list.extend(SwordphishUser.objects.exclude())
        else:
            regs = self.regions()
            users_list.append(self)
            for region in regs:
                usrs = region.members.all()
                for user in usrs:
                    if user not in users_list:
                        users_list.append(user)
        return users_list

    def is_staff_or_admin(self):
        if self.user.is_staff:
            return True

        return bool(Entity.objects.filter(admins__user__username=self.user.username))

    def can_be_edited(self, current_user):
        if current_user.swordphishuser == self:
            return True

        if self.is_staff_or_admin():
            return current_user.is_staff

        if self in current_user.swordphishuser.subordinates():
            return True

        return False

    class Meta:
        ordering = ['user__last_name', 'user__first_name', 'user__email']


def get_admin():
    return SwordphishUser.objects.filter(user__is_superuser=True)[0]



class Entity(models.Model):
    name = models.CharField(max_length=200)
    admins = models.ManyToManyField(SwordphishUser)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']



class Region(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(SwordphishUser, through='RegionMembership')
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    def __str__(self):
        return "%s / %s" % (self.entity.name, self.name)

    def prettyname(self):
        return "%s / %s" % (self.entity.name, self.name)

    class Meta:
        ordering = ["entity__name", 'name']



class RegionMembership(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    user = models.ForeignKey(SwordphishUser, on_delete=models.CASCADE)

    def __str__(self):
        return "%s => %s / %s" % (self.user.user.email, self.region.entity.name, self.region.name)
