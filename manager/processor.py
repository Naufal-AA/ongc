from .models import *
from adminuser.models import *
from itertools import chain
from django.db.models import Sum

def desoption(request):
    return {'desoption': Designation.objects.all().order_by('id')}

def desoptionlist(request):
    emailList = []
    emailList += [des.name for des in Designation.objects.all()]
    desoptionlist = str(emailList)
    desoptionlist = desoptionlist[2:-2]
    return {'desoptionlist' : desoptionlist}

def pendingrequest(request):
    return {'pendingrequest': KeyRequest.objects.filter(close="False").count()}

def employee(request):
    return {'employee': Employee.objects.count()}

def department(request):
    return {'department': Designation.objects.count()}

def transportationcount(request):
    transportationcount = Transportation.objects.all().count()
    return {'transportationcount': transportationcount }

def storycount(request):
    return {'storycount': Stories.objects.all().count()}

def newscount(request):
    return {'newscount': News.objects.all().count()}

def project(request):
    project = Project.objects.count()
    if project%5 == 0 or project<5:
        project = project
    else:
        project = str(project - project % 5) + '+'
    return {'project': project}

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

def payment(request):
    result = Payment.objects.aggregate(sum=Sum('amount'))
    try:
        payment = human_format(float(result["sum"]))
    except Exception:
        payment = 0.00
    return {'payment': payment}


def notificationcount(request):
    works = WorksOn.objects.filter(status='Completed').all().order_by('-id')
    request1 = KeyRequest.objects.filter(close=False).all().order_by('-id')
    notificationlist = sorted(chain(works, request1),key=lambda instance: instance.update, reverse=True)

    return {'notificationcount': len(notificationlist)}

def notificationlists(request):
    works = WorksOn.objects.filter(status='Completed').all().order_by('-id')
    request1 = KeyRequest.objects.filter(close=False).all().order_by('-id')
    notificationlists = sorted(chain(works, request1),key=lambda instance: instance.update, reverse=True)

    return {'notificationlists': notificationlists[:5]}

def mystory(request):
    mystory = Stories.objects.all().order_by('-id')
    return {'mystory': mystory}

def mynews(request):
    mynews = News.objects.all().order_by('-id')
    return {'mynews': mynews}