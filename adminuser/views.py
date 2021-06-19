from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from .models import *
from manager.models import Transportation, User, Admin, Employee, Project, Designation, Payment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.core.files.storage import FileSystemStorage
from django.utils.encoding import smart_str
from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from manager.decorators import *

import os
from os.path import dirname, join
from math import *
import imghdr

def about(request):
    return render(request, "admin/growth.html")

def technology(request):
    return render(request, "admin/technology.html")

def history(request):
    return render(request, "admin/history.html")

def vision(request):
    return render(request, "admin/vision.html")

def contact(request):
    return render(request, "admin/contact.html")

def sustainability(request):
    return render(request, "admin/environment.html")

def carbon(request):
    return render(request, "admin/carbon.html")

def health(request):
    return render(request, "admin/health.html")

def investor(request):
    return render(request, "admin/policies.html")

def notices(request):
    return render(request, "admin/notices.html")

def media(request):
    return render(request, "admin/bulletin.html")

def pay(request):
    return render(request, "admin/pay.html")

@unauthenticated_user
def admin(request):
    if request.method == "POST":
        if 'admin' in request.POST:
            admin = request.POST.get("admin")

            try:
                adminuser = User.objects.get(username=admin)

                image = adminuser.admin_user.image

                if image:
                    image = adminuser.admin_user.image.url
                else:
                    image = False
                if adminuser:
                    type = adminuser.type
                    if type == "ADM":
                        context = {
                            "entry": admin,
                            "image": image
                        }
                        return render(request, "admin/adminlogin.html", context)
                    else:
                        return render(request, "admin/adminlogin.html", {"admin" :True})
                else:
                    return render(request, "admin/adminlogin.html", {"admin" :True})
            except Exception as e:
                return render(request, "admin/adminlogin.html", {"admin" :True})
    
        if 'password' in request.POST:
            username =request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                if user.type == 'ADM':
                    login(request, user)
                    return redirect('admindashboard')
                
                else:
                    context = {
                    "message": True,
                    "entry": username,
                    }
                    return render(request, "admin/adminlogin.html", context)

            else:
                context = {
                    "message": True,
                    "entry": username,
                }
                return render(request, "admin/adminlogin.html", context)

    else:
        return render(request, "admin/adminlogin.html", {"admin" :True})


@login_required(login_url='admin')
@admin_only
def changeadmin(request, change):
    change = change
    
    if request.method =="POST":
        if 'Change-Username2' in request.POST:
            modal = '''
                    <script>
                        $(document).ready(function(){
                            $('#change-user-name2').modal('show');
                        })
                    </script>
                    '''
            username = request.POST['currentusername2']
            newuser = request.POST['changeusername2']

            try:
                user = User.objects.get(username=username)
                
                if User.objects.filter(username=newuser).first():
                    context = {
                        "modaladmin" : modal,
                        "messageclass2": "danger",
                        "messageheader2": "Username is already Exists",
                        "message2": "Account Creation was unsuccessful. Please Enter different username",
                    }
                    return render(request, "admin/admindashboard.html", context)
                
                user.username = newuser
                user.save()

                '''
                context = {
                    "modaladmin" : modal,
                    "messageclass2": "success",
                    "messageheader2": "Username Changed",
                    "message2": "Your username has been changed",
                }
                return render(request, "admin/admindashboard.html", context)
                '''
                return redirect('admindashboard')
            except Exception:
                context = {
                    "modaladmin" : modal,
                    "messageclass2": "danger",
                    "messageheader2": "OOPS",
                    "message2": "Something went wrong! Please check your username!",
                }
                return render(request, "admin/admindashboard.html", context)
        
        if 'changepassword2' in request.POST:
            modal = '''
                    <script>
                        $(document).ready(function(){
                            $('#change-password2').modal('show');
                        })
                    </script>
                    '''
            cpassword = request.POST['cpassword2']
            npassword = request.POST['npassword2']

            try:
                if request.user.is_authenticated:
                    username = request.user.username
                    user = User.objects.get(username=username)
                
                    check = user.check_password(cpassword)

                    if check:
                        user.set_password(npassword)
                        user.save()

                        '''
                        context = {
                            "modaladmin" : modal,
                            "messageclass3": "success",
                            "messageheader3": "Password Changed",
                            "message3": "Your Password has been changed",
                        }
                        return render(request, "admin/admindashboard.html", context)
                        '''
                        return redirect('admindashboard')
                    else:
                        context = {
                        "modaladmin" : modal,
                        "messageclass3": "danger",
                        "messageheader3": "OOPS",
                        "message3": "Your current Password is wrong!",
                    }
                    return render(request, "admin/admindashboard.html", context)
                else:
                    return redirect('/')

            except Exception:
                context = {
                    "modaladmin" : modal,
                    "messageclass3": "danger",
                    "messageheader3": "OOPS",
                    "message3": "Something went wrong! Please check your username!",
                }
                return render(request, "admin/admindashboard.html", context)
    else:
        if request.user.is_authenticated:
            if change == 'Change-Username':
                modal =   '''
                                <script>
                                    $(document).ready(function(){
                                        $('#change-user-name2').modal('show');
                                    })
                                </script>
                                '''
                context = {
                        "modaladmin" : modal,
                }
                return render(request, "admin/admindashboard.html", context)
            
            if change == 'Change-Password':
                modal =   '''
                                <script>
                                    $(document).ready(function(){
                                        $('#change-password2').modal('show');
                                    })
                                </script>
                                '''
                context = {
                        "modaladmin" : modal,
                }
                return render(request, "admin/admindashboard.html", context)
        else:
            return redirect('/')


@login_required(login_url='admin')
@admin_only
def admindashboard(request):
    if request.method == "POST":
        if 'storybutton' in request.POST:
            stitle = request.POST.get('stitle')
            description = request.POST.get('description')
            
            try:
                storyfile = request.FILES['storyfile']
            except MultiValueDictKeyError:
                storyfile = ''

            try:
                story = Stories.objects.create(title=stitle, image=storyfile, description=description)
                story.save()
                context = {
                    "messageclass": "success",
                    "messageheader": "All done",
                    "message": "Successfully uploaded!",
                }
                return render(request, "admin/admindashboard.html", context)
            except IntegrityError:
                context = {
                    "messageclass": "danger",
                    "messageheader": "Title is already Exists",
                    "message": "Story Upload was unsuccessful. Please Enter different title!",
                }
                return render(request, "admin/admindashboard.html", context)
    
        if 'newsbutton' in request.POST:
            ntitle = request.POST.get('ntitle')
            ndescription = request.POST.get('ndescription')

            try:
                news = News.objects.create(title=ntitle, description=ndescription)
                news.save()
                context = {
                    "messageclass1": "success",
                    "messageheader1": "All done",
                    "message1": "Successfully uploaded!",
                }
                return render(request, "admin/admindashboard.html", context)
            except IntegrityError:
                context = {
                    "messageclass1": "danger",
                    "messageheader1": "Title is already Exists",
                    "message1": "News Upload was unsuccessful. Please Enter different title!",
                }
                return render(request, "admin/admindashboard.html", context)
        
        if request.user.is_authenticated:
            user = get_object_or_404(User, username=request.user.username)
            adm = get_object_or_404(Admin, user=user)
            try:
                myuploadfile = request.FILES['myuploadfile']
            except MultiValueDictKeyError:
                myuploadfile = ''

            modal = '''
                <script>
                    $(document).ready(function(){
                        $('#admin-profile').modal('show');
                    })
                </script>
                '''
            context = {
                'modaladmin' : modal,
            }

            if not myuploadfile=='':
                check_image = imghdr.what(myuploadfile)
                if not (check_image== "jpg" or check_image== "jpeg" or check_image== "png"):
                    return render(request, "admin/admindashboard.html", context)
                else:
                    try:
                        old_file = adm.image
                        if not old_file.name == myuploadfile:
                            if os.path.isfile(old_file.path):
                                os.remove(old_file.path)
                    except Exception:
                        pass
                    adm.image = myuploadfile
                    adm.save()
                    return render(request, "admin/admindashboard.html", context)

    else:
        return render(request, "admin/admindashboard.html")

@login_required(login_url='admin')
@admin_only
def adminstories(request):
    stories = Stories.objects.all().order_by('-id')

    p = Paginator(stories, 5) #10
    page_num = request.GET.get('Page', 1)
    seeall = request.GET.get('View')
    query = request.GET.get('search', None)

    if seeall == 'seeall':
        seeall = True
        page = Stories.objects.all().order_by('-id')

    else:
        try:
            page = p.page(page_num)

        except PageNotAnInteger:
            page = p.page(1)
        except EmptyPage:
            page = p.page(p.num_pages)
    
    if request.method == "POST":
        if 'deletestory' in request.POST:
            id = int(request.POST.get('deleteid'))
            try:
                stories = Stories.objects.get(id=id)
                title = stories.title
                fs = FileSystemStorage()
                ROOT_DIR = dirname(dirname(__file__))
                output_path = join(ROOT_DIR, 'media')
                filename = stories.image.name
                fullpath=os.path.join(output_path, filename)
                fs.delete(fullpath)
                stories.delete()

                context = {
                    'stories' : page,
                    'seeall' : seeall,
                    "messageclass" : "success",
                    "messageheader" : "Deleted Successfully!",
                    "message"   : f"The {title} has been removed",
                }
                return render(request, "admin/adminstories.html", context)
            except Exception:
                context = {
                    'stories' : page,
                    'seeall' : seeall,
                    "messageclass" : "danger",
                    "messageheader" : "OOPS!",
                    "message"   : "Something went wrong! please try again later",
                }
                return render(request, "admin/adminstories.html", context)
    
    elif query is not None:
        if query == "":
            page = p.page(1)
            context = {
                'stories' : page,
                'seeall' : seeall,
            }
            return render(request, "admin/adminstories.html", context)

        storylist = Stories.objects.filter(( Q(title__icontains=query) | Q(description__icontains=query)| Q(timestamp__icontains=query))).all()
            
        context = {
            'stories' : storylist,
            'seeall' : True,
        }
        return render(request, "admin/adminstories.html", context)


    context = {
        'stories' : page,
        'seeall' : seeall,
    }
    return render(request, "admin/adminstories.html", context)

@login_required(login_url='admin')
@admin_only
def adminnews(request):
    news = News.objects.all().order_by('-id')

    p = Paginator(news, 5) #10
    page_num = request.GET.get('Page', 1)
    seeall = request.GET.get('View')
    query = request.GET.get('search', None)

    if seeall == 'seeall':
        seeall = True
        page = News.objects.all().order_by('-id')
       
    else:
        try:
            page = p.page(page_num)

        except PageNotAnInteger:
            page = p.page(1)
        except EmptyPage:
            page = p.page(p.num_pages)
    
    if request.method == "POST":
        if 'deletenews' in request.POST:
            id = int(request.POST.get('deleteid'))
            try:
                news = News.objects.get(id=id)
                title = news.title
                news.delete()

                context = {
                    'news' : page,
                    'seeall' : seeall,
                    "messageclass" : "success",
                    "messageheader" : "Deleted Successfully!",
                    "message"   : f"The {title} has been removed",
                }
                return render(request, "admin/adminnews.html", context)
            except Exception:
                context = {
                    'news' : page,
                    'seeall' : seeall,
                    "messageclass" : "danger",
                    "messageheader" : "OOPS!",
                    "message"   : "Something went wrong! please try again later",
                }
                return render(request, "admin/adminnews.html", context)
    
    elif query is not None:
        if query == "":
            page = p.page(1)
            context = {
                'news' : page,
                'seeall' : seeall,
            }
            return render(request, "admin/adminnews.html", context)

        newslist = News.objects.filter(( Q(title__icontains=query) | Q(description__icontains=query)| Q(timestamp__icontains=query))).all()
            
        context = {
            'news' : newslist,
            'seeall' : True,
        }
        return render(request, "admin/adminnews.html", context)

    context = {
        'news' : page,
        'seeall' : seeall,
    }
    return render(request, "admin/adminnews.html", context)

@login_required(login_url='admin')
@admin_only
def adminproject(request):
    projects = Project.objects.all().order_by('-id')

    p = Paginator(projects, 5) #10
    page_num = request.GET.get('Page', 1)
    seeall = request.GET.get('View')
    query = request.GET.get('search', None)

    if seeall == 'seeall':
        seeall = True
        page = Project.objects.all().order_by('-id')
    
    elif query is not None:
        if query == "":
            page = p.page(1)
            context = {
                'projects' : page,
                'seeall' : seeall,
            }
            return render(request, "admin/adminproject.html", context) 

        projectlist = Project.objects.filter(( Q(title__icontains=query) | Q(duedate__icontains=query)| Q(priority__icontains=query))).all()
            
        context = {
            'projects' : projectlist,
            'seeall' : True,
        }
        return render(request, "admin/adminproject.html", context) 
    
    else:
        try:
            page = p.page(page_num)

        except PageNotAnInteger:
            page = p.page(1)
        except EmptyPage:
            page = p.page(p.num_pages)


    context = {
        'projects' : page,
        'seeall' : seeall,
    }
    return render(request, "admin/adminproject.html", context)

@login_required(login_url='admin')
@admin_only
def admindownload(request, id):
    try:
        project = Project.objects.get(id=id)
        file = project.projectfile.name
        filename = os.path.basename(file)
        filename = filename[:-4]

        response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(filename)
        response['X-Sendfile'] = smart_str(file)
        return response

    except Project.DoesNotExist:
        return HttpResponseNotFound('The requested file was not found in our server.')
            

@login_required(login_url='admin')
@admin_only
def adminemployee(request):
    employee = Employee.objects.all().order_by('-id')

    p = Paginator(employee, 10)
    page_num = request.GET.get('Page', 1)
    seeall = request.GET.get('View')
    query = request.GET.get('search', None)

    if seeall == 'seeall':
        seeall = True
        page = Employee.objects.all().order_by('-id')
    
    elif query is not None:
        if query == "":
            page = p.page(1)
            context = {
                'employees' : page,
                'seeall' : seeall,
            }
            return render(request, "admin/adminemployee.html", context)

        myemployeelist = Employee.objects.filter(( Q(user__first_name__icontains=query) & Q(user__last_name__icontains=query)| \
            Q(user__email__icontains=query) | Q(user__gender__icontains=query) | Q(designation__code__icontains=query) | Q(designation__name__icontains=query))).distinct()
            
        context = {
            'employees' : myemployeelist,
            'seeall' : True,
        }
        return render(request, "admin/adminemployee.html", context) 
    
    else:
        try:
            page = p.page(page_num)

        except PageNotAnInteger:
            page = p.page(1)
        except EmptyPage:
            page = p.page(p.num_pages)


    context = {
        'employees' : page,
        'seeall' : seeall,
    }
    return render(request, "admin/adminemployee.html", context)

@login_required(login_url='admin')
@admin_only
def admindepartment(request):
    if request.method == "POST":
        code = request.POST.get('depcode')
        name = request.POST.get('depname')

        try:
            dept = Designation.objects.create(code=code, name=name)
            dept.save()
            context = {
                "messageclass": "success",
                "messageheader": "All done",
                "message": "Successfully added department!",
                "departments" : Designation.objects.all().order_by('-id'),
            }
            return render(request, "admin/admindepartment.html", context)
        except IntegrityError:
            context = {
                "messageclass": "danger",
                "messageheader": "Department is already exists!",
                "message": "department Upload was unsuccessful. Please Enter different department name!",
                "departments" : Designation.objects.all().order_by('-id'),
            }
            return render(request, "admin/admindepartment.html", context)
    else:
        context = {
            "departments" : Designation.objects.all().order_by('id').reverse,
        }
    return render(request, "admin/admindepartment.html", context)

@login_required(login_url='admin')
@admin_only
def admintransport(request):
    transport = Transportation.objects.all().order_by('-id')

    p = Paginator(transport, 5) #10
    page_num = request.GET.get('Page', 1)
    seeall = request.GET.get('View')
    query = request.GET.get('search', None)

    if seeall == 'seeall':
        seeall = True
        page = Transportation.objects.all().order_by('-id')
    
    elif query is not None:
        if query == "":
            page = p.page(1)
            context = {
                'transport' : page,
                'seeall' : seeall,
            }
            return render(request, "admin/admintransport.html", context)

        mytransportlist = Transportation.objects.filter(( Q(project__icontains=query) | Q(place__icontains=query)| \
            Q(employee__icontains=query) | Q(transportnumber__icontains=query) | Q(timestamp__icontains=query))).distinct()

        context = {
            'transport' : mytransportlist,
            'seeall' : True,
        }
        return render(request, "admin/admintransport.html", context)
    
    else:
        try:
            page = p.page(page_num)

        except PageNotAnInteger:
            page = p.page(1)
        except EmptyPage:
            page = p.page(p.num_pages)


    context = {
        'transport' : page,
        'seeall' : seeall,
    }
    return render(request, "admin/admintransport.html", context)

@login_required(login_url='admin')
@admin_only
def adminpayment(request):
    payment = Payment.objects.all().order_by('-id')

    p = Paginator(payment, 5) #10
    page_num = request.GET.get('Page', 1)
    seeall = request.GET.get('View')
    query = request.GET.get('search', None)

    if seeall == 'seeall':
        seeall = True
        page = Payment.objects.all().order_by('-id')
    
    elif query is not None:
        if query == "":
            page = p.page(1)
            context = {
                'payments' : page,
                'seeall' : seeall,
            }
            return render(request, "admin/adminpayment.html", context)

        mypaymentlist = Payment.objects.filter(( Q(project__icontains=query) | Q(projectplace__icontains=query)| \
            Q(employee__icontains=query) | Q(amount__icontains=query) | Q(timestamp__icontains=query))).distinct()

        context = {
            'payments' : mypaymentlist,
            'seeall' : True,
        }
        return render(request, "admin/adminpayment.html", context)
    
    else:
        try:
            page = p.page(page_num)

        except PageNotAnInteger:
            page = p.page(1)
        except EmptyPage:
            page = p.page(p.num_pages)


    context = {
        'payments' : page,
        'seeall' : seeall,
    }
    return render(request, "admin/adminpayment.html", context)


@login_required(login_url='admin')
def editstory(request, id):
    story = get_object_or_404(Stories, id=id)

    context = {
        "editstory" : story,
    }

    if request.method =="POST":
        if 'storyeditbutton' in request.POST:
            hiddenid = request.POST.get('hiddenid')
        
            story = get_object_or_404(Stories, id=hiddenid)

            stitle = request.POST.get('stitle')
            description = request.POST.get('description')
            
            try:
                storyfile = request.FILES['storyfile']
            except MultiValueDictKeyError:
                storyfile = ''

            stitle = story.title if not stitle else stitle
            description = story.description if not description else description
            storyfile = story.image if not storyfile else storyfile

            try:
                story.title = stitle
                story.description = description
                story.image = storyfile 
                story.save()
                context = {
                    "messageclass": "success",
                    "messageheader": "All done",
                    "message": "Successfully Updated!",
                }
                return render(request, "admin/admindashboard.html", context)
            except IntegrityError:
                context = {
                    "messageclass": "danger",
                    "messageheader": "Title is already Exists",
                    "message": "Story Upload was unsuccessful. Please Enter different title!",
                }
                return render(request, "admin/admindashboard.html", context)

    return render(request, "admin/admindashboard.html", context)


@login_required(login_url='admin')
def editnews(request, id):
    news = get_object_or_404(News, id=id)

    context = {
        "editnews" : news,
    }

    if request.method =="POST":
        if 'newsupdatebutton' in request.POST:
            hiddenid = request.POST.get('hiddenid1')
        
            news = get_object_or_404(News, id=hiddenid)

            ntitle = request.POST.get('ntitle')
            ndescription = request.POST.get('ndescription')
            
            ntitle = news.title if not ntitle else ntitle
            ndescription = news.description if not ndescription else ndescription

            try:
                news.title = ntitle
                news.description = ndescription
                news.save()
                context = {
                    "messageclass1": "success",
                    "messageheader1": "All done",
                    "message1": "Successfully Updated!",
                }
                return render(request, "admin/admindashboard.html", context)
            except IntegrityError:
                context = {
                    "messageclass1": "danger",
                    "messageheader1": "Title is already Exists",
                    "message1": "News Upload was unsuccessful. Please Enter different title!",
                }
                return render(request, "admin/admindashboard.html", context)

    return render(request, "admin/admindashboard.html", context)

@login_required(login_url='admin')
def logoutadmin(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))