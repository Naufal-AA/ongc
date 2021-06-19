from django.contrib import admin
from .models import *


# Register your models here.
class designationSetting(admin.ModelAdmin):
    #list_display = [field.name for field in Designation._meta.get_fields()]
    list_display = ('code', 'name', 'timestamp')

class userSettings(admin.ModelAdmin):
    list_display = ('username', 'email','name', 'gender', 'phone', 'type')
    def name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

class employeeSettings(admin.ModelAdmin):
    list_display = ('name', 'email', 'username', 'phone','gender', 'designation', 'group_password', 'is_verified', 'active')
    def name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
    def email(self, obj):
        return obj.user.email
    def username(self, obj):
        return obj.user.username
    def phone(self, obj):
        return obj.user.phone
    def gender(self, obj):
        return obj.user.gender
    def designation(self, obj):
        return obj.designation.name
    def group_password(self, obj):
        return obj.designation.code
    
class managerSettings(admin.ModelAdmin):
    list_display = ('name', 'email', 'username', 'phone','gender', 'image', 'designation')
    def name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
    def email(self, obj):
        return obj.user.email
    def username(self, obj):
        return obj.user.username
    def phone(self, obj):
        return obj.user.phone
    def gender(self, obj):
        return obj.user.gender

class adminSettings(admin.ModelAdmin):
    list_display = ('name', 'email', 'username', 'phone','gender', 'image', 'designation')
    def name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
    def email(self, obj):
        return obj.user.email
    def username(self, obj):
        return obj.user.username
    def phone(self, obj):
        return obj.user.phone
    def gender(self, obj):
        return obj.user.gender

class projectSetting(admin.ModelAdmin):
    #list_display = [field.name for field in Project._meta.get_fields()]
    list_display = ('title', 'duedate', 'forwardto', 'priority', 'projectfile', 'key' )

class worksSettings(admin.ModelAdmin):
    list_display = ('employee', 'designation', 'projectname', 'status')
    def employee(self, obj):
        return f'{obj.empid.user.first_name} {obj.empid.user.last_name}'
    def designation(self, obj):
        return obj.empid.designation.name
    def projectname(self, obj):
        return obj.projectid.title

class keyrequestSettings(admin.ModelAdmin):
    list_display = ('employee', 'designation', 'projectname', 'reason', 'permit', 'close')
    def employee(self, obj):
        return f'{obj.empid.user.first_name} {obj.empid.user.last_name}'
    def designation(self, obj):
        return obj.empid.designation.name
    def projectname(self, obj):
        return obj.projectid.title

class paymentSetting(admin.ModelAdmin):
    list_display = [field.name for field in Payment._meta.get_fields()]

class transportSetting(admin.ModelAdmin):
    list_display = [field.name for field in Transportation._meta.get_fields()]

admin.site.register(User, userSettings)
admin.site.register(Employee, employeeSettings)
admin.site.register(Manager, managerSettings)
admin.site.register(Admin, adminSettings)
admin.site.register(Project, projectSetting)
admin.site.register(Designation, designationSetting)
admin.site.register(KeyRequest, keyrequestSettings)
admin.site.register(WorksOn, worksSettings)
admin.site.register(Payment, paymentSetting)
admin.site.register(Transportation, transportSetting)