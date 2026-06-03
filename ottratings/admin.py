from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from ottratings.models import Users, Ratings, Comments, Contact

class UsersInLine(admin.StackedInline):
    model=Users
    can_delete = False
    verbose_name: 'Users'
    
class CustomizedUserAdmin(UserAdmin):
    inlines=(UsersInLine,)

admin.site.unregister(User)
admin.site.register(User,CustomizedUserAdmin)
    
admin.site.register(Ratings)
admin.site.register(Users)
admin.site.register(Comments)
admin.site.register(Contact)