from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

import datetime



'''
The Group_Resources table will contain all information about a given project.
Atributes:
    - URI
    - tenant(repo)
    - Account Name
    - username (glint user for that cloud)
    - password (glint user pw for that cloud)
'''
class Group_Resources(models.Model):
    cloud_name = models.CharField(primary_key=True, max_length=20)
    group_name = models.CharField(max_length=32)
    auth_url = models.CharField(max_length=128, default="")
    tenant = models.CharField(max_length=128, default="")
    #credentials? How to encrypt?
    username = models.CharField(max_length=20)
    password = models.TextField()
    project_domain_name = models.CharField(max_length=20, default="Default")
    user_domain_name = models.CharField(max_length=20, default="Default")
    region = models.CharField(max_length=20, null=True, default=None)
    cloud_type = models.CharField(max_length=64, null=True, default="Openstack")
    # need to have control options in the table for csv2 compatibility
    '''
    extrayaml = models.CharField(null=True, default=None)
    cacertificate = models.CharField(null=True, default=None)
    server_meta_ctl =  models.IntegerField()
    instances_ctl = models.IntegerField()
    personality_ctl =  models.IntegerField()
    image_meta_ctl =  models.IntegerField()
    personality_size_ctl =  models.IntegerField()
    ram_ctl =  models.IntegerField()
    server_groups_ctl =  models.IntegerField()
    security_group_rules_ctl =  models.IntegerField()
    keypairs_ctl =  models.IntegerField()
    security_groups_ctl =  models.IntegerField()
    server_group_members_ctl =  models.IntegerField()
    floating_ips_ctl =  models.IntegerField()
    cores_ctl =  models.IntegerField()
    '''

    class Meta:
        db_table = 'csv2_group_resources'


    def __str__(self):
        return self.account_name + ": " + self.tenant

'''
The Glint User table provides the second layer of authentication and provides room for future developments
of alternative authenication methods (ssh, user/pw, etc)
'''
class Glint_User(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=128) #keeping this long for hashes
    # May need another table for these instead of just a generic string field
    # authentication method currently isn't used for anything and may be able to be pruned
    #authentication_method = models.CharField(max_length=32, default="x509")
    cert_cn = models.CharField(max_length=64, default="")
    active_group = models.CharField(max_length=64, default="", null=True, blank=True)
    join_date = models.DateField(default=datetime.date.today, null=True)

    class Meta:
        db_table = 'csv2_user'


    def __str__(self):
        return "%s" % (self.user_name)



class Group(models.Model):
    group_name = models.CharField(max_length=32)
    def __str__(self):
        return "%s" % (self.group_name)

'''
The User_Account table will contain the correlation between users and the accounts they have access to.
Attributes:
    - Project Name
    - User  (...glint user?)
    - Date last used
'''
class User_Group(models.Model):
    group_name = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(Glint_User, on_delete=models.CASCADE)
    last_used = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return "%s: %s" % (self.group_name, self.user)


