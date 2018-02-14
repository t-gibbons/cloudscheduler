from django.contrib import admin

from csv2.models import user as Glint_User
from .models import Group_Resources, Group, User_Group

admin.site.register(Group_Resources)
admin.site.register(Glint_User)
admin.site.register(Group)
admin.site.register(User_Group)
