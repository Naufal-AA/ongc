from django.db import models

class Stories(models.Model):
    title = models.CharField(max_length=300, unique=True)
    image = models.FileField(upload_to='Stories/%Y/%m/%d/', null=True)
    description = models.CharField(default='', max_length=1500)
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)
    update = models.DateTimeField(auto_now = True, auto_now_add = False)

    def __str__(self):
        return f"{self.title}"

class News(models.Model):
    title = models.CharField(default='', max_length=300, unique=True)
    description = models.CharField(default='', max_length=1500)
    timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)
    update = models.DateTimeField(auto_now = True, auto_now_add = False)

    def __str__(self):
        return f"{self.title}"