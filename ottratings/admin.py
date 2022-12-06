from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from ottratings.models import *
# Register your models here.
class UsersInLine(admin.StackedInline):
    model=Users
    can_delete = False
    verbose_name: 'Users'
    
class CustomizedUserAdmin(UserAdmin):
    inlines=(UsersInLine,)

admin.site.unregister(User)
admin.site.register(User,CustomizedUserAdmin)
    
    
admin.site.register(Views)
admin.site.register(Ratings)
admin.site.register(Web)
admin.site.register(Users)
admin.site.register(Comments)
admin.site.register(Season)
admin.site.register(Episode)
admin.site.register(Available_on)
admin.site.register(Categories)
admin.site.register(Languages)
admin.site.register(Cat_list)
admin.site.register(Lang_list)
admin.site.register(plat_list)
admin.site.register(Contact)