from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _



class Designation(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=300, unique=True)
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)

    def __str__(self):
        return f"{self.name}"

class User(AbstractUser):
    class Types(models.TextChoices):
        EMP = 'Emp', _('Employee')
        MAN = "MAN", _('Manager')
        ADM = "ADM", _('Admin')

    gender = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=300, blank=True)
    type = models.CharField(max_length=3, choices=Types.choices, default=Types.MAN)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
    
    def __str__(self):
        return f"{self.username} - {self.type}"
    

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name="emp_user")
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE, related_name="designation") 
    #designation = models.OneToOneField(Designation, on_delete = models.CASCADE, related_name="designation")
    image = models.ImageField(upload_to='Employee Profile/', blank=True)
    is_verified = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    auth_token = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)
    update = models.DateTimeField(auto_now = True, auto_now_add = False)
    
    def __str__(self):
        return f"{self.user} - {self.designation}"

    # These two auto-delete files from filesystem when they are unneeded:


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name="manager_user")
    image = models.ImageField(upload_to='Manager Profile/', blank=True)
    designation = models.CharField(max_length=300, default='Managing Director')
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)
    update = models.DateTimeField(auto_now = True, auto_now_add = False)

    def __str__(self):
        return f"{self.user} - {self.designation}"

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE,  related_name="admin_user")
    image = models.ImageField(upload_to='Admin Profile/', blank=True)
    designation = models.CharField(max_length=300, default='Admin')
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)
    update = models.DateTimeField(auto_now = True, auto_now_add = False)

    def __str__(self):
        return f"{self.user} - {self.designation}"

class Project(models.Model):
    title =  models.CharField(max_length=200, unique=True)
    duedate = models.DateField()
    forwardto = models.CharField(max_length=500)
    priority = models.CharField(max_length=100, default='low')
    projectfile = models.FileField(upload_to='Projects/%Y/%m/%d/', null=True)
    key = models.CharField(max_length=100, default='')
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)
    update = models.DateTimeField(auto_now = True, auto_now_add = False)

    def __str__(self):
        return f"{self.title} - ({self.duedate}) -{self.priority}"
     
class WorksOn(models.Model):
    empid = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="employee") 
    projectid = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project") 
    status = models.CharField(max_length=100, default='pending')
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)
    update = models.DateTimeField(auto_now = True, auto_now_add = False)

    def __str__(self):
        return f"{self.empid} - ({self.projectid}) -{self.status}"

class KeyRequest(models.Model):
    empid = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="emp_request") 
    projectid = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_request")
    reason = models.CharField(max_length=50, default='')
    permit = models.BooleanField(default=False)
    close = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)
    update = models.DateTimeField(auto_now = True, auto_now_add = False)

    def __str__(self):
        return f"{self.empid} - ({self.projectid}) -{self.permit}"

class Payment(models.Model):
    project = models.CharField(max_length=200)
    projectplace = models.CharField(max_length=200)
    employee = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)

    def __str__(self):
        return f"{self.project} - ({self.employee}) -{self.amount}"
        
class Transportation(models.Model):
    project = models.CharField(max_length=200)
    place = models.CharField(max_length=200)
    employee = models.CharField(max_length=50)
    transportnumber = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)

    def __str__(self):
        return f"{self.transportnumber}"