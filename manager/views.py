from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import F, Q, Count
from itertools import chain
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from hashids import Hashids
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.utils.dateparse import parse_date
from django.conf.global_settings import DEFAULT_FROM_EMAIL
from django.core.mail import EmailMultiAlternatives
from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from .decorators import *
from .AES import *

import os
from os.path import dirname, join
from math import *
import imghdr

def error_404(request, exception):
    return render(request,'manager/error404.html')

@unauthenticated_user
def loginmanager(request):
    modalscript =   '''
                    <script>
                        $(document).ready(function(){
                            $('#manager-login').modal('show');
                        })
                    </script>
                    '''

    if request.method == "POST":
        if 'signinmanager' in request.POST:
            # Attempt to sign user in
            username = request.POST.get("manageruser")
            password = request.POST.get("managerpassword")

            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                if user.type == 'MAN':
                    login(request, user)
                    return redirect('dashboard')

                else:
                    context = {
                        "modalscript": modalscript,
                        "messageclass": "danger",
                        "messageheader": "Invalid Credentials!",
                        "message": "Please verify your username and password and try agian!!",
                    }
                    return render(request, "manager/index.html", context)
            else:
                context = {
                    "modalscript": modalscript,
                    "messageclass": "danger",
                    "messageheader": "Invalid Credentials!",
                    "message": "Please verify your username and password and try agian!!",
                }
                return render(request, "manager/index.html", context)
    
        if 'resetmanager' in request.POST:
            forgotuser =  request.POST.get("forgotusermanager")
            forgotemail =  request.POST.get("forgotemailmanager")
            
            modalscript =   '''
                            <script>
                                $(document).ready(function(){
                                    $('#forgot-password').modal('show');
                                })
                            </script>
                            '''
            
            try:
                user = User.objects.filter(username=forgotuser).filter(email=forgotemail).first()
                hashids = Hashids(min_length=32)
                token = hashids.encode(user.id)
                #ints = hashids.decode(token)

                subject = "Reset Your Password - ONGC"
                text_content = ""

                html_content = f'''<center>
                                    <div style="background: #ebebeb; width: 500px; padding:20px 40px;">
                                        <div style="color: #454545;font-family: 'Poppins'; font-style: normal; font-weight: 300; font-display: swap; src: url(https://fonts.gstatic.com/s/poppins/v15/pxiByp8kv8JHgFVrLDz8Z11lFc-K.woff2) format('woff2'); unicode-range: U+0900-097F, U+1CD0-1CF6, U+1CF8-1CF9, U+200C-200D, U+20A8, U+20B9, U+25CC, U+A830-A839, U+A8E0-A8FB;">
                                            <h1 style="background: #34394d; color: whitesmoke; padding: 30px; text-align:start; font-size: 24px; margin-bottom: 0;">
                                                <img src="https://i.ibb.co/DpvtfcQ/adminlogo.png" alt="adminlogo" border="0" width="40px" height="40px" valign="middle" style="margin-top:-10px"> Oil and Natural Gas Corporation          
                                            </h1> 
                                            <div style="background: #fefefe; width: 500px; height: 400px; padding-top: 20px;">
                                                <!--<img src="https://cdn.dribbble.com/users/1354544/screenshots/3305658/_dribbble_comp.gif" width="70%" alt="">-->
                                                <h2 style="text-align: start; padding-left:50px;color: #363434; font-weight: 300; ">Hi {user.first_name} {user.last_name},</h2>
                                                <p style="text-align: start; padding-left:50px; margin-bottom: 30px;">A request has been received to change the password for your ONGC account </p>
                                                <a href="https://ongc.herokuapp.com/Managing-Director/Reset-Password/{token}" style="font-weight:500; text-decoration: none; color: whitesmoke; background: #198754; padding: 10px 30px; margin-left: 20px; border-radius: 6px;" onMouseOver="this.style.backgroundColor='#116d43'"
                                                onMouseOut="this.style.backgroundColor='#198754'" >Reset Password</a>
                                                <p style="text-align: start; padding-left:50px; margin-top: 30px; margin-bottom: 50px;">if you did not initiate this request, please contact us immediately at <a href="" style="text-decoration: none; color: #198754;" onMouseOver="this.style.color='#198754'" onMouseOut="this.style.color='#198754a8'" >support@ongc.com</a></p>
                                                <p style="text-align: start; padding-left:50px; margin-bottom: 0;">Thank you,</p>
                                                <p style="text-align: start; padding-left:50px;margin-top: 0;">ONGC Team</p>
                                            </div>
                                            <br>
                                            <small style="color: #b7b7b7; font-size: x-small;">sent by Oil and Natural Gas Corporation</small><br>
                                            <small style="color: #b7b7b7; font-size: x-small;">No. 5A- 5B, Nelson Mandela Road, Vasant Kunj, New Delhi, 110070</small>
                                        </div>
                                    </div>
                                </center>
                                '''

                from_mail = DEFAULT_FROM_EMAIL
                to_mail = [user.email]

                # if send_mail(subject,message,from_mail,to_mail):
                msg = EmailMultiAlternatives(subject, text_content, from_mail, to_mail)
                msg.attach_alternative(html_content, "text/html")

                if msg.send():
                    context = {
                        "modalscript": modalscript,
                        "message": True,
                    }
                    return render(request, "manager/index.html", context)
                
                else:
                    context = {
                        "modalscript": modalscript,
                        "message": True,
                    }
                    return render(request, "manager/index.html", context)

            except Exception:
                context = {
                    "modalscript": modalscript,
                    "message": True,
                }
                return render(request, "manager/index.html", context)
        
    else:
        context = {
                "modalscript": modalscript,
            }
        return render(request, "manager/index.html", context)

@login_required(login_url='loginmanager')
def logoutmanager(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@unauthenticated_user
def resetmanager(request, auth_token):
    modalscript =   '''
                    <script>
                        $(document).ready(function(){
                            $('#forgot-password').modal('show');
                        })
                    </script>
                    '''

    if request.method == "POST":
        resetpassword = request.POST['resetpasswordmanager']
        auth_token = auth_token
        hashids = Hashids(min_length=32)
    
        try:
            id = hashids.decode(auth_token)
            id = id[0]
            user = User.objects.get(id=id)

            if user:
                user.set_password(resetpassword)
                user.save()
                context = {
                    "modalscript" : modalscript,
                    "messageclass": "success",
                    "messageheader": "Password Changed.",
                    "message": "Your Password has been Changed",
                    "reset" : True,
                }
                return render(request, "manager/index.html", context)
            else:
                context = {
                    "modalscript" : modalscript,
                    "messageclass": "danger",
                    "messageheader": "OOPS",
                    "message": "Something Wrong!!",
                    "reset" : True,
                }
                return render(request, "manager/index.html", context)
        except Exception:
            context = {
                "modalscript" : modalscript,
                "messageclass": "danger",
                "messageheader": "OOPS",
                "message": "Something Wrong!!",
                "reset" : True,
            }
            return render(request, "manager/index.html", context)

    else:
        auth_token = auth_token
        context = {
            "modalscript" : modalscript,
            "reset" : True,
            "auth_token" : auth_token
        }
        return render(request, "manager/index.html", context)

@login_required(login_url='loginmanager')
@manager_only
def changemanager(request, change):
    change = change
    
    if request.method =="POST":
        if 'Change-Username1' in request.POST:
            modal = '''
                    <script>
                        $(document).ready(function(){
                            $('#change-user-name1').modal('show');
                        })
                    </script>
                    '''
            username = request.POST['currentusernamemanager']
            newuser = request.POST['changeusernamemanager']

            try:
                user = User.objects.get(username=username)
                
                if User.objects.filter(username=newuser).first():
                    context = {
                        "modalmanager" : modal,
                        "messageclass": "danger",
                        "messageheader": "Username is already Exists",
                        "message": "Account Creation was unsuccessful. Please Enter different username",
                    }
                    return render(request, "manager/manager-dashboard.html", context)
                
                user.username = newuser
                user.save()

                '''
                context = {
                    "modalmanager" : modal,
                    "messageclass": "success",
                    "messageheader": "Username Changed",
                    "message": "Your username has been changed",
                }
                return render(request, "manager/manager-dashboard.html", context)
                '''
                return redirect('dashboard')

            except Exception:
                context = {
                    "modalmanager" : modal,
                    "messageclass": "danger",
                    "messageheader": "OOPS",
                    "message": "Something went wrong! Please check your username!",
                }
                return render(request, "manager/manager-dashboard.html", context)
        
        if 'changepassword1' in request.POST:
            modal = '''
                    <script>
                        $(document).ready(function(){
                            $('#change-password1').modal('show');
                        })
                    </script>
                    '''
            cpassword = request.POST['cpassword1']
            npassword = request.POST['npassword1']

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
                            "modalmanager" : modal,
                            "messageclass1": "success",
                            "messageheader1": "Password Changed",
                            "message1": "Your Password has been changed",
                        }
                        return render(request, "manager/manager-dashboard.html", context)
                        '''

                        return redirect('dashboard')
                    else:
                        context = {
                        "modalmanager" : modal,
                        "messageclass1": "danger",
                        "messageheader1": "OOPS",
                        "message1": "Your current Password is wrong!",
                    }
                    return render(request, "manager/manager-dashboard.html", context)
                else:
                    return redirect('/')

            except Exception:
                context = {
                    "modalmanager" : modal,
                    "messageclass1": "danger",
                    "messageheader1": "OOPS",
                    "message1": "Something went wrong! Please check your username!",
                }
                return render(request, "manager/manager-dashboard.html", context)
    else:
        if request.user.is_authenticated:
            if change == 'Change-Username':
                modal =   '''
                            <script>
                                $(document).ready(function(){
                                    $('#change-user-name1').modal('show');
                                })
                            </script>
                            '''
                context = {
                        "modalmanager" : modal,
                }
                return render(request, "manager/manager-dashboard.html", context)
            
            if change == 'Change-Password':
                modal =   '''
                                <script>
                                    $(document).ready(function(){
                                        $('#change-password1').modal('show');
                                    })
                                </script>
                                '''
                context = {
                        "modalmanager" : modal,
                }
                return render(request, "manager/manager-dashboard.html", context)
        else:
            return redirect('/')


@login_required(login_url='loginmanager')
@manager_only
def dashboard(request):
    workson = WorksOn.objects.filter(Q(status='In Progress') | Q(status='Completed')).order_by('-id')[:20]

    p = Paginator(workson, 6)
    page_num = request.GET.get('Page', 1)
    seeall = request.GET.get('View')

    if seeall == 'seeall':
        seeall = True
        page = WorksOn.objects.all().order_by('-id')

    else:
        try:
            page = p.page(page_num)

        except PageNotAnInteger:
            page = p.page(1)
        except EmptyPage:
            page = p.page(p.num_pages)
    
    if request.method == "POST":
        if request.user.is_authenticated:
            user = get_object_or_404(User, username=request.user.username) # Manager User
            man = get_object_or_404(Manager, user=user) # Employee id

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
                'modalmanager' : modal,
                'workson' : page,
                'seeall' : seeall,
            }

            if not myuploadfile=='':
                check_image = imghdr.what(myuploadfile)
                if not (check_image== "jpg" or check_image== "jpeg" or check_image== "png"):
                    return render(request, "manager/manager-dashboard.html", context)
                else:
                    try:
                        old_file = man.image
                        if not old_file.name == myuploadfile:
                            if os.path.isfile(old_file.path):
                                os.remove(old_file.path)
                    except Exception:
                        pass
                    man.image = myuploadfile
                    man.save()
                    return render(request, "manager/manager-dashboard.html", context)
                
    else:
        context = {
            'workson' : page,
            'seeall' : seeall,
        }
        return render(request, "manager/manager-dashboard.html", context)


@login_required(login_url='loginmanager')
@manager_only
def addproject(request):
    if request.method == "POST" and request.FILES['selectfile']:
        title = request.POST.get('title')
        duedate = request.POST.get('duedate')
        forward = request.POST.get('forward')
        priority = request.POST.get('priority')
        selectfile = request.FILES['selectfile']
        duedate = parse_date(duedate)

        try:
            if Project.objects.filter(title=title).first():
                context = {
                    "messageclass" : "danger",
                    "messageheader": "Title is already Exists",
                    "message": "Project Upload was unsuccessful. Please Enter different title",
                }
                return render(request, "manager/manager-addproject.html", context)

            fs = FileSystemStorage()
            filename = fs.save(selectfile.name, selectfile)
            
            ROOT_DIR = dirname(dirname(__file__))
            output_path = join(ROOT_DIR, 'media')
            fullpath=os.path.join(output_path, filename)

            key = User.objects.make_random_password(length=32)
            enc = Encryptor(key)
            enc.encrypt_file(fullpath)
            #enc.decrypt_file(str(fullpath)+".enc")

            encfile = os.path.join('media', filename) + ".enc"
            fullpath = fullpath + ".enc"

            forwardlist = forward.split(",")
            emailList = []

            for i in range(len(forwardlist)):
                try:
                    designation = Designation.objects.get(name=forwardlist[i])
                    emailList += [emp.user.email for emp in Employee.objects.all().filter(designation=designation).filter(is_verified=True)]
                except Exception as e:
                    #print(e)
                    pass
        
            mydate = duedate.strftime("%d %b, %Y")
            subject = f"Private Key for {title} - ONGC"
            text_content = ""

            html_content =f'''<center>
                                <div style="background: #ebebeb; width: 500px; padding:20px 40px;">
                                    <div style="color: #454545;font-family: 'Poppins'; font-style: normal; font-weight: 300; font-display: swap; src: url(https://fonts.gstatic.com/s/poppins/v15/pxiByp8kv8JHgFVrLDz8Z11lFc-K.woff2) format('woff2'); unicode-range: U+0900-097F, U+1CD0-1CF6, U+1CF8-1CF9, U+200C-200D, U+20A8, U+20B9, U+25CC, U+A830-A839, U+A8E0-A8FB;">
                                        <h1 style="background: #34394d; color: whitesmoke; padding: 30px; text-align:start; font-size: 24px; margin-bottom: 0;">
                                            <img src="https://i.ibb.co/DpvtfcQ/adminlogo.png" alt="adminlogo" border="0" width="40px" height="40px" valign="middle" style="margin-top:-10px"> Oil and Natural Gas Corporation          
                                        </h1> 
                                        <div style="background: #fefefe; width: 500px; height: 520px; padding-top: 20px;">
                                            <img src="https://cdn.dribbble.com/users/1354544/screenshots/3305658/_dribbble_comp.gif" width="70%" alt="">
                                            <h3 style="text-align: start; padding-left:60px;margin-bottom: 0;color: #762a2a; ">{title}</h3>
                                            <p style="margin:0; margin-left:10px; padding:3px 5px;border-radius: 4px; color: #ebebeb; font-size: x-small;display: inline-block;background-color: #dc3545;">Due date: {mydate} </p>
                                            <p style="margin:0; margin-left:200px; padding:3px 5px;border-radius: 4px; color: #ebebeb; font-size: x-small;display: inline-block;background-color: #0d6efd;">Priority: {priority}</p>
                                            <br>
                                            <img src="https://www.freeiconspng.com/thumbs/key-icon/black-key-symbol-icon-6.png" alt="" style="height: 25px;margin-left: -275px;margin-top: 20px;vertical-align: top;">
                                            <h3 style="display: inline-block; padding: 0;padding-top: 5px;color: #444444;">{key}</h3>
                                            <p style="border: 1px dashed #dc3545 ; display: block; padding: 10px;margin:10px 20px;text-align: start;color: #dc3545;font-size: small;">
                                                <img src="https://i.ibb.co/2dFB0Yh/unnamed.png" alt="" style="height: 20px;vertical-align: top;">
                                                Your Private key gives access to your project's firebase services. Keep it confidential and never store it in a public repository
                                            </p>
                                            <p style="text-align: start; padding-left:20px; font-size: smaller;margin-right: 10px;">Store this file securely, because your new key can't be recovered if lost</p>
                                        </div>
                                        <br>
                                        <small style="color: #b7b7b7; font-size: x-small;">sent by Oil and Natural Gas Corporation</small><br>
                                        <small style="color: #b7b7b7; font-size: x-small;">No. 5A- 5B, Nelson Mandela Road, Vasant Kunj, New Delhi, 110070</small>
                                    </div>
                                </div>
                            </center>
                            '''
            
            from_mail = DEFAULT_FROM_EMAIL
            to_mail = emailList

            msg = EmailMultiAlternatives(subject, text_content, from_mail, bcc=to_mail)
            msg.attach_alternative(html_content, "text/html")

            if msg.send():
                project = Project.objects.create(
                        title=title, duedate=duedate, forwardto=forward, 
                        priority=priority, key=key)
                project.save()

                with open(encfile, 'rb') as fi:
                    project.projectfile = File(fi, name=os.path.basename(fi.name))
                    project.save()

                context = {
                    "messageclass": "success",
                    "messageheader": "All done",
                    "message": "Your project has been successfully uploaded and send the key to corresponding peoples!",
                }
                fs = FileSystemStorage()
                fs.delete(fullpath)
                return render(request, "manager/manager-addproject.html", context)
        
        except Exception as e:
            #print(e)
            pass

    else:
        return render(request, "manager/manager-addproject.html")

@login_required(login_url='loginmanager')
@manager_only
def viewproject(request):

    viewproject = Project.objects.all().order_by('-id')

    p = Paginator(viewproject, 5)
    page_num = request.GET.get('Page', 1)
    seeall = request.GET.get('View')
    query = request.GET.get('search', None)

    if seeall == 'seeall':
        seeall = True
        page = Project.objects.all().order_by('-id')

    else:
        try:
            page = p.page(page_num)

        except PageNotAnInteger:
            page = p.page(1)
        except EmptyPage:
            page = p.page(p.num_pages)
    
    if request.method == "POST":
        if 'deleteproject' in request.POST:
            id = int(request.POST.get('deleteid'))
            try:
                project = Project.objects.get(id=id)
                title = project.title
                fs = FileSystemStorage()
                ROOT_DIR = dirname(dirname(__file__))
                output_path = join(ROOT_DIR, 'media')
                filename = project.projectfile.name
                fullpath=os.path.join(output_path, filename)
                fs.delete(fullpath)
                project.delete()

                context = {
                    'viewproject' : page,
                    'seeall' : seeall,
                    "messageclass" : "success",
                    "messageheader" : "Deleted Successfully!",
                    "message"   : f"The {title} has been removed",
                }
                return render(request, "manager/manager-viewproject.html", context)
            except Exception:
                context = {
                    'viewproject' : page,
                    'seeall' : seeall,
                    "messageclass" : "danger",
                    "messageheader" : "OOPS!",
                    "message"   : "Something went wrong! please try again later",
                }
                return render(request, "manager/manager-viewproject.html", context)

    elif query is not None:
        if query == "":
            page = p.page(1)
            context = {
                'viewproject' : page,
                'seeall' : seeall,
            }
            return render(request, "manager/manager-viewproject.html", context)

        viewproject = Project.objects.filter(( Q(title__icontains=query) | Q(duedate__icontains=query)| \
            Q(forwardto__icontains=query) | Q(priority__icontains=query) | Q(projectfile__icontains=query)| \
                Q(timestamp__icontains=query))).all()
            
        context = {
            'viewproject' : viewproject,
            'seeall' : True,
        }
        return render(request, "manager/manager-viewproject.html", context)
    
    elif query is None:
        context = {
        'viewproject' : page,
        'seeall' : seeall,            
        }
        return render(request, "manager/manager-viewproject.html", context)
    
    else:
        context = {
            'viewproject' : page,
            'seeall' : seeall,
        }
        return render(request, "manager/manager-viewproject.html", context)


@login_required(login_url='loginmanager')
@manager_only
def editproject(request, title, id):
    try:
        project = Project.objects.filter(id=id).filter(title=title).first()

        context = {
            'addproject': project
        }
        if not project:
            raise Http404("Does Not Exist")
        
        if request.method =="POST":
            if 'myeditproject' in request.POST:
                idhidden = request.POST.get('idhidden')
                titlehidden = request.POST.get('titlehidden')
            
                project = Project.objects.filter(id=idhidden).filter(title=titlehidden).first()

                title = request.POST.get('title')
                duedate = request.POST.get('duedate')
                forward = request.POST.get('forward')
                priority = request.POST.get('priority')
                try:
                    selectfile = request.FILES['selectfile']
                except MultiValueDictKeyError:
                    selectfile =""

                title = project.title if not title else title
                duedate = project.duedate if not duedate else parse_date(duedate)
                forward = project.forwardto if not forward else forward
                priority = project.priority if not priority else priority
                selectfile = project.projectfile if not selectfile else selectfile

                try:
                    if project.projectfile.name == selectfile:
                        key = project.key   
                    
                    else: 
                        fs = FileSystemStorage()
                        filename = fs.save(selectfile.name, selectfile)
                        
                        ROOT_DIR = dirname(dirname(__file__))
                        output_path = join(ROOT_DIR, 'media')
                        fullpath=os.path.join(output_path, filename)

                        key = User.objects.make_random_password(length=32)
                        enc = Encryptor(key)
                        enc.encrypt_file(fullpath)
                        #enc.decrypt_file(str(fullpath)+".enc")

                        encfile = os.path.join('media', filename) + ".enc"
                        fullpath = fullpath + ".enc"

                    forwardlist = forward.split(",")
                    emailList = []

                    for i in range(len(forwardlist)):
                        try:
                            designation = Designation.objects.get(name=forwardlist[i])
                            emailList += [emp.user.email for emp in Employee.objects.all().filter(designation=designation).filter(is_verified=True)]
                        except Exception as e:
                            #print(e)
                            pass
                
                    mydate = duedate.strftime("%d %b, %Y")
                    subject = f"Private Key for {title} - ONGC"
                    text_content = ""

                    html_content =f'''<center>
                                        <div style="background: #ebebeb; width: 500px; padding:20px 40px;">
                                            <div style="color: #454545;font-family: 'Poppins'; font-style: normal; font-weight: 300; font-display: swap; src: url(https://fonts.gstatic.com/s/poppins/v15/pxiByp8kv8JHgFVrLDz8Z11lFc-K.woff2) format('woff2'); unicode-range: U+0900-097F, U+1CD0-1CF6, U+1CF8-1CF9, U+200C-200D, U+20A8, U+20B9, U+25CC, U+A830-A839, U+A8E0-A8FB;">
                                                <h1 style="background: #34394d; color: whitesmoke; padding: 30px; text-align:start; font-size: 24px; margin-bottom: 0;">
                                                    <img src="https://i.ibb.co/DpvtfcQ/adminlogo.png" alt="adminlogo" border="0" width="40px" height="40px" valign="middle" style="margin-top:-10px"> Oil and Natural Gas Corporation          
                                                </h1> 
                                                <div style="background: #fefefe; width: 500px; height: 520px; padding-top: 20px;">
                                                    <img src="https://cdn.dribbble.com/users/1354544/screenshots/3305658/_dribbble_comp.gif" width="70%" alt="">
                                                    <h3 style="text-align: start; padding-left:60px;margin-bottom: 0;color: #762a2a; ">{title}</h3>
                                                    <p style="margin:0; margin-left:10px; padding:3px 5px;border-radius: 4px; color: #ebebeb; font-size: x-small;display: inline-block;background-color: #dc3545;">Due date: {mydate} </p>
                                                    <p style="margin:0; margin-left:200px; padding:3px 5px;border-radius: 4px; color: #ebebeb; font-size: x-small;display: inline-block;background-color: #0d6efd;">Priority: {priority}</p>
                                                    <br>
                                                    <img src="https://www.freeiconspng.com/thumbs/key-icon/black-key-symbol-icon-6.png" alt="" style="height: 25px;margin-left: -275px;margin-top: 20px;vertical-align: top;">
                                                    <h3 style="display: inline-block; padding: 0;padding-top: 5px;color: #444444;">{key}</h3>
                                                    <p style="border: 1px dashed #dc3545 ; display: block; padding: 10px;margin:10px 20px;text-align: start;color: #dc3545;font-size: small;">
                                                        <img src="https://i.ibb.co/2dFB0Yh/unnamed.png" alt="" style="height: 20px;vertical-align: top;">
                                                        Your Private key gives access to your project's firebase services. Keep it confidential and never store it in a public repository
                                                    </p>
                                                    <p style="text-align: start; padding-left:20px; font-size: smaller;margin-right: 10px;">Store this file securely, because your new key can't be recovered if lost</p>
                                                </div>
                                                <br>
                                                <small style="color: #b7b7b7; font-size: x-small;">sent by Oil and Natural Gas Corporation</small><br>
                                                <small style="color: #b7b7b7; font-size: x-small;">No. 5A- 5B, Nelson Mandela Road, Vasant Kunj, New Delhi, 110070</small>
                                            </div>
                                        </div>
                                    </center>
                                    '''
                    
                    from_mail = DEFAULT_FROM_EMAIL
                    to_mail = emailList

                    msg = EmailMultiAlternatives(subject, text_content, from_mail, bcc=to_mail)
                    msg.attach_alternative(html_content, "text/html")

                    if msg.send():
                        project.title=title
                        project.duedate=duedate
                        project.forwardto=forward 
                        project.priority=priority
                        project.key=key
                        project.save()

                        if not project.projectfile.name == selectfile:
                            with open(encfile, 'rb') as fi:
                                project.projectfile = File(fi, name=os.path.basename(fi.name))
                                project.save()
                            fs = FileSystemStorage()
                            fs.delete(fullpath)
                        
                        works = WorksOn.objects.filter(projectid=project).filter(Q(status='In Progress') | Q(status='Completed')).all()

                        for p in works:
                            p.status = "Pending"
                            p.save()

                        context = {
                            "messageclass": "success",
                            "messageheader": "All done",
                            "message": "Your project has been successfully uploaded and send the key to corresponding peoples!",
                        }
                        
                        return render(request, "manager/manager-addproject.html", context)
                except IntegrityError:
                    context = {
                        "messageclass" : "danger",
                        "messageheader": "Title is already Exists",
                        "message": "Project Upload was unsuccessful. Please Enter different title",
                    }
                    return render(request, "manager/manager-addproject.html", context)
                except Exception as e:
                    print(e)
                    
        return render(request, "manager/manager-addproject.html", context)

    except Exception:
        raise Http404("Does not Exist")

@login_required(login_url='loginmanager')
@manager_only
def viewemployee(request):
    emp = Employee.objects.all().order_by('designation')

    p = Paginator(emp, 10)
    page_num = request.GET.get('Page', 1)
    seeall = request.GET.get('View')
    query = request.GET.get('search', None)

    if seeall == 'seeall':
        seeall = True
        page = Employee.objects.all().order_by('designation')
    
    elif query is not None:
        if query == "":
            page = p.page(1)
            context = {
                'employeelist' : page,
                'seeall' : seeall,
            }
            return render(request, "manager/manager-viewemployee.html", context)

        employeelist = Employee.objects.filter(( Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query)| \
            Q(user__email__icontains=query) | Q(user__gender__icontains=query) | Q(user__phone__icontains=query)| \
                Q(designation__code__icontains=query) | Q(designation__name__icontains=query) | Q(timestamp__icontains=query))).all()
            
        context = {
            'employeelist' : employeelist,
            'seeall' : True,
        }
        return render(request, "manager/manager-viewemployee.html", context)
    
    else:
        try:
            page = p.page(page_num)

        except PageNotAnInteger:
            page = p.page(1)
        except EmptyPage:
            page = p.page(p.num_pages)


    context = {
        'employeelist' : page,
        'seeall' : seeall,
    }
    return render(request, "manager/manager-viewemployee.html", context)
    

@login_required(login_url='loginmanager')
@manager_only
def viewdepartment(request):
    #{'department': 'value', 'employee': value}
    designation = Designation.objects.values(department=F('name')).annotate(employee=Count('designation'))
    #{'department': 'value', 'totalproject': value}
    total = WorksOn.objects.values(department=F('empid__designation__name')).annotate(totalproject=Count('status'))
    #{'status': 'value', 'department': 'value', 'total': value}
    mycompleted = WorksOn.objects.values('status',department=F('empid__designation__name')).annotate(total=Count('status'))

    #{'department': 'value', 'completed':'value'/'inprogress':'value'/'pending':'value'}
    for i in mycompleted:
        if i["status"] == "Completed":
            i["completed"] = i["total"]
        
        if i["status"] == "In Progress":
            i["inprogress"] = i["total"]
        
        if i["status"] == "Pending":
            i["pending"] = i["total"]
        
        del i["status"]
        del i["total"]


    test_key = 'department'

    #designation = {'department': 'value', 'employee': value, 'completed': value, 'inprogress': value, 'pending': value}
    for sub in designation:
        for i in mycompleted:
            if sub[test_key] == i[test_key]:
                if 'completed' in i.keys():
                    sub["completed"] = i["completed"]
                
                if 'inprogress' in i.keys():
                    sub["inprogress"] = i["inprogress"]
                
                if 'pending' in i.keys():
                    sub["pending"] = i["pending"]
                        
            
    #designation = {'department': 'value', 'employee': value, 'completed': value, 'inprogress': value, 'pending': value, 'totalproject': value}
    for sub1 in designation:
        temp = next((itm for itm in total if sub1[test_key] == itm[test_key]), None)
        
        if(temp):
            sub1.update(temp)
    
    context = {
        'designationlist' : designation
    }
    return render(request, "manager/manager-viewdepartment.html", context)

@login_required(login_url='loginmanager')
@manager_only
def viewrequest(request):
    context = {
        'requestpending' : KeyRequest.objects.filter(close="False").all().order_by('-id'),
        'requestpast' : KeyRequest.objects.filter(close="True").all().order_by('-id'),
    }
    return render(request, "manager/manager-viewrequest.html", context)

@login_required(login_url='loginmanager')
@manager_only
def keypermit(request, id, permit):
    try:
        keyrequest = KeyRequest.objects.get(id=id)

        if permit=="granted":
            title = keyrequest.projectid.title
            duedate = keyrequest.projectid.duedate
            priority = keyrequest.projectid.priority
            key = keyrequest.projectid.key
            emailList = keyrequest.empid.user.email
            mydate = duedate.strftime("%d %b, %Y")
            subject = f"Private Key for {title} - ONGC"
            text_content = ""

            html_content =f'''<center>
                                <div style="background: #ebebeb; width: 500px; padding:20px 40px;">
                                    <div style="color: #454545;font-family: 'Poppins'; font-style: normal; font-weight: 300; font-display: swap; src: url(https://fonts.gstatic.com/s/poppins/v15/pxiByp8kv8JHgFVrLDz8Z11lFc-K.woff2) format('woff2'); unicode-range: U+0900-097F, U+1CD0-1CF6, U+1CF8-1CF9, U+200C-200D, U+20A8, U+20B9, U+25CC, U+A830-A839, U+A8E0-A8FB;">
                                        <h1 style="background: #34394d; color: whitesmoke; padding: 30px; text-align:start; font-size: 24px; margin-bottom: 0;">
                                            <img src="https://i.ibb.co/DpvtfcQ/adminlogo.png" alt="adminlogo" border="0" width="40px" height="40px" valign="middle" style="margin-top:-10px"> Oil and Natural Gas Corporation          
                                        </h1> 
                                        <div style="background: #fefefe; width: 500px; height: 520px; padding-top: 20px;">
                                            <img src="https://cdn.dribbble.com/users/1354544/screenshots/3305658/_dribbble_comp.gif" width="70%" alt="">
                                            <h3 style="text-align: start; padding-left:60px;margin-bottom: 0;color: #762a2a; ">{title}</h3>
                                            <p style="margin:0; margin-left:10px; padding:3px 5px;border-radius: 4px; color: #ebebeb; font-size: x-small;display: inline-block;background-color: #dc3545;">Due date: {mydate} </p>
                                            <p style="margin:0; margin-left:200px; padding:3px 5px;border-radius: 4px; color: #ebebeb; font-size: x-small;display: inline-block;background-color: #0d6efd;">Priority: {priority}</p>
                                            <br>
                                            <img src="https://www.freeiconspng.com/thumbs/key-icon/black-key-symbol-icon-6.png" alt="" style="height: 25px;margin-left: -275px;margin-top: 20px;vertical-align: top;">
                                            <h3 style="display: inline-block; padding: 0;padding-top: 5px;color: #444444;">{key}</h3>
                                            <p style="border: 1px dashed #dc3545 ; display: block; padding: 10px;margin:10px 20px;text-align: start;color: #dc3545;font-size: small;">
                                                <img src="https://i.ibb.co/2dFB0Yh/unnamed.png" alt="" style="height: 20px;vertical-align: top;">
                                                Your Private key gives access to your project's firebase services. Keep it confidential and never store it in a public repository
                                            </p>
                                            <p style="text-align: start; padding-left:20px; font-size: smaller;margin-right: 10px;">Store this file securely, because your new key can't be recovered if lost</p>
                                        </div>
                                        <br>
                                        <small style="color: #b7b7b7; font-size: x-small;">sent by Oil and Natural Gas Corporation</small><br>
                                        <small style="color: #b7b7b7; font-size: x-small;">No. 5A- 5B, Nelson Mandela Road, Vasant Kunj, New Delhi, 110070</small>
                                    </div>
                                </div>
                            </center>
                            '''
            
            from_mail = DEFAULT_FROM_EMAIL
            to_mail = [emailList]

            msg = EmailMultiAlternatives(subject, text_content, from_mail, bcc=to_mail)
            msg.attach_alternative(html_content, "text/html")

            if msg.send():
                keyrequest.permit = True
                keyrequest.close = True
                keyrequest.save()
        else:
            keyrequest.permit = False
            keyrequest.close = True
            keyrequest.save()
        
        context = {
            'requestpending' : KeyRequest.objects.filter(close="False").all().order_by('-id'),
            'requestpast' : KeyRequest.objects.filter(close="True").all().order_by('-id'),
        }
        return render(request, "manager/manager-viewrequest.html", context) 
    except Exception:
        pass


@login_required(login_url='loginmanager')
@manager_only
def notification(request):
    works = WorksOn.objects.filter(status='Completed').all().order_by('-id')
    request1 = KeyRequest.objects.filter(close=False).all().order_by('-id')
    notificationlist = sorted(chain(works, request1),key=lambda instance: instance.update, reverse=True)
    context = {
        'notificationlist' : notificationlist,
    }
    return render(request, "manager/manager-notification.html", context)


@login_required(login_url='loginmanager')
@manager_only
def searchmanager(request):
    query = request.GET.get('q', None)
    if query is not None:
        myemployeelist = Employee.objects.filter(( Q(user__first_name__icontains=query) & Q(user__last_name__icontains=query)| \
            Q(user__email__icontains=query) | Q(user__gender__icontains=query) | Q(user__phone__icontains=query)| \
                Q(designation__code__icontains=query) | Q(designation__name__icontains=query) | Q(timestamp__icontains=query))).distinct()
        
        myprojectlist = Project.objects.filter(( Q(title__icontains=query) | Q(duedate__icontains=query)| \
            Q(forwardto__icontains=query) | Q(priority__icontains=query) | Q(projectfile__icontains=query)| \
                Q(timestamp__icontains=query))).distinct()

        myworklist = WorksOn.objects.filter(( Q(empid__user__first_name__icontains=query) & Q(empid__user__last_name__icontains=query)| \
                Q(empid__designation__code__icontains=query) | Q(empid__designation__name__icontains=query) | Q(projectid__title__icontains=query) | \
                    Q(status__icontains=query) | Q(timestamp__icontains=query) | Q(update__icontains=query))).distinct()
        
        mykeyrequestlist = KeyRequest.objects.filter(( Q(empid__user__first_name__icontains=query) & Q(empid__user__last_name__icontains=query)| \
                Q(empid__designation__code__icontains=query) | Q(empid__designation__name__icontains=query) | Q(projectid__title__icontains=query) | \
                    Q(reason__icontains=query) | Q(timestamp__icontains=query))).distinct()

        mypaymentlist = Payment.objects.filter(( Q(project__icontains=query) | Q(projectplace__icontains=query)| \
            Q(employee__icontains=query) | Q(amount__icontains=query) | Q(timestamp__icontains=query))).distinct()
        
        mytransportlist = Transportation.objects.filter(( Q(project__icontains=query) | Q(place__icontains=query)| \
            Q(employee__icontains=query) | Q(transportnumber__icontains=query) | Q(timestamp__icontains=query))).distinct()
        

        totalcount = len(myemployeelist) + len(myprojectlist) + len(myworklist) + len(mykeyrequestlist) + len(mypaymentlist) + len(mytransportlist)
        
        if query == "":
            totalcount = 0
        context = {
            "myemployeelist" : myemployeelist,
            "myprojectlist" : myprojectlist,
            "myworklist" : myworklist,
            "mykeyrequestlist" : mykeyrequestlist,
            "mypaymentlist" : mypaymentlist,
            "mytransportlist" : mytransportlist,
            "totalcount" : totalcount,
            "query" : query,
        }
        return render(request, "manager/manager-search.html", context)
    
    else:
        context = {
            "searchhome" : True,
        }
    return render(request, "manager/manager-search.html", context)
