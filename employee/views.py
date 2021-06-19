from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.db.models import Q, Sum
from .models import *
from manager.models import Designation, Payment, Transportation, User, Employee, Project, WorksOn, KeyRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import Group

from hashids import Hashids
from django.core.files.storage import FileSystemStorage
from django.conf.global_settings import DEFAULT_FROM_EMAIL
from django.core.mail import EmailMultiAlternatives
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.encoding import smart_str
from manager.decorators import *
from manager.AES import *
from .downloadpdf import *

import os
import uuid
from os.path import dirname, join
import imghdr


def index(request):
    return render(request, "manager/index.html")

@unauthenticated_user
def register(request):
    modalscript =   '''
                    <script>
                        $(document).ready(function(){
                            $('#employee-register').modal('show');
                        })
                    </script>
                    '''

    if request.method == "POST":
        last = ''
        first = request.POST["fname"]
        last = request.POST["lname"]
        gender = request.POST["gender"]
        email = request.POST["email"]
        designation = request.POST["designation"]

        phone_number = request.POST["phone"]
        username = request.POST["username"]
        password = request.POST["password"]
        image = ''
        try:
            code = request.POST["code"]
        except MultiValueDictKeyError:
            code = '+91'
        phone = str(code) + str(phone_number)
        auth_token = str(uuid.uuid4())

        try:
            if User.objects.filter(username=username).first():

                context = {
                    "modalscript": modalscript,
                    "messageclass" : "danger",
                    "messageheader": "Username is already Exists",
                    "message": "Account Creation was unsuccessful. Please Enter different username",
                }
                return render(request, "manager/index.html", context)

            if User.objects.filter(first_name=first, last_name= last).first():
                context = {
                    "modalscript": modalscript,
                    "messageclass" : "danger",
                    "messageheader": "You are already Registered",
                    "message": "Account Creation was unsuccessful. Please Login using your username and password",
                }
                return render(request, "manager/index.html", context)


            subject = "Verify your Email - ONGC"
            text_content = ""

            html_content =f'''<center>
                                <div style="background: whitesmoke; width: 500px; padding:20px 40px;">
                                    <div style="color: #454545;font-family: 'Poppins'; font-style: normal; font-weight: 300; font-display: swap; src: url(https://fonts.gstatic.com/s/poppins/v15/pxiByp8kv8JHgFVrLDz8Z11lFc-K.woff2) format('woff2'); unicode-range: U+0900-097F, U+1CD0-1CF6, U+1CF8-1CF9, U+200C-200D, U+20A8, U+20B9, U+25CC, U+A830-A839, U+A8E0-A8FB;">
                                        <h1 style="background: #34394d; color: whitesmoke; padding: 30px; text-align:start; font-size: 24px; font-weight: 500; margin-bottom: 0;">
                                            <img src="https://i.ibb.co/DpvtfcQ/adminlogo.png" alt="adminlogo" border="0" width="40px" height="40px" valign="middle" style="margin-top:-10px"> Oil and Natural Gas Corporation            
                                        </h1> 
                                        <div style="background: #f6fdfd; width: 500px; height: 480px; padding-top: 20px;">
                                            <img src="https://cdn.dribbble.com/users/1551941/screenshots/6346538/thankyoudribble.gif" width="70%" alt="">
                                            <h3 style="text-align: start; padding-left:60px; font-weight: 600;">Hey {first} {last}!</h3>
                                            <p style="text-align: start; padding-left:60px; font-weight: 400;">Please Verify your email address. so we know that its really you!</p>
                                            <br><a href="http://127.0.0.1:8000/Employee/verify/{auth_token}" style="font-weight:500; text-decoration: none; color: whitesmoke; background: #198754; padding: 10px 30px; margin-left: 20px; border-radius: 6px;" onMouseOver="this.style.backgroundColor='#116d43'"
                                            onMouseOut="this.style.backgroundColor='#198754'" >Verify Email</a>
                                        </div>
                                        <br>
                                        <small style="color: #b7b7b7; font-size: x-small;">sent by Oil and Natural Gas Corporation</small><br>
                                        <small style="color: #b7b7b7; font-size: x-small;">No. 5A- 5B, Nelson Mandela Road, Vasant Kunj, New Delhi, 110070</small>
                                    </div>
                                </div>
                            </center>
                            '''

            from_mail = DEFAULT_FROM_EMAIL
            to_mail = [email]

            # if send_mail(subject,message,from_mail,to_mail):
            msg = EmailMultiAlternatives(subject, text_content, from_mail, to_mail)
            msg.attach_alternative(html_content, "text/html")

            if msg.send():
                designation = Designation.objects.get(name=designation)
                user = User.objects.create_user(username, email, password, first_name=first, last_name=last, type=User.Types.EMP, gender=gender, phone=phone)
                user.save()
                emp = Employee.objects.create(user=user, designation=designation, auth_token=auth_token, image=image)
                emp.save()

                context = {
                    "modalscript": modalscript,
                    "mail_message": True,
                    "email_to": email,
                }
                return render(request, "manager/index.html", context)
            
            else:
                context = {
                    "modalscript": modalscript,
                    "messageclass" : "danger",
                    "messageheader": "You are email is not valid",
                    "message": "Account Creation was unsuccessful. Please check your mail id again!",
                }
                return render(request, "manager/index.html", context)
        except Exception as e:
            #print(e)
            pass
    
    else:
        context = {
            "modalscript": modalscript,
        }
        return render(request, "manager/index.html", context)

@unauthenticated_user
def verify(request, auth_token):
    try:
        emp = Employee.objects.filter(auth_token=auth_token).first()

        modalscript = '''
                        <script>
                            $(document).ready(function(){
                                $('#employee-login').modal('show');
                            })
                        </script>
                    '''

        if emp:
            if emp.is_verified:

                context = {
                    "modalscript": modalscript,
                    "messageclass": "danger",
                    "messageheader": "Already Verified!",
                    "message": "Someone else has already verified!. Please Login using your username and password!",
                }
                return render(request, "manager/index.html", context)

            subject = "Your Group Password - ONGC"
            text_content = ""

            html_content = f'''<center>
                                    <div style="background: #ebebeb; width: 500px; padding:20px 40px;">
                                        <div style="color: #454545;font-family: 'Poppins'; font-style: normal; font-weight: 300; font-display: swap; src: url(https://fonts.gstatic.com/s/poppins/v15/pxiByp8kv8JHgFVrLDz8Z11lFc-K.woff2) format('woff2'); unicode-range: U+0900-097F, U+1CD0-1CF6, U+1CF8-1CF9, U+200C-200D, U+20A8, U+20B9, U+25CC, U+A830-A839, U+A8E0-A8FB;">
                                            <h1 style="background: #34394d; color: whitesmoke; padding: 30px; text-align:start; font-size: 24px; margin-bottom: 0;">
                                                <img src="https://i.ibb.co/DpvtfcQ/adminlogo.png" alt="adminlogo" border="0" width="40px" height="40px" valign="middle" style="margin-top:-10px"> Oil and Natural Gas Corporation          
                                            </h1> 
                                            <div style="background: #f9f9f9; width: 500px; height: 480px; padding-top: 20px;">
                                                <img src="https://cdn.dribbble.com/users/1405642/screenshots/3045094/043_success-mail.gif" width="70%" alt="">
                                                <h3 style="text-align: start; padding-left:60px;">Hey {emp.user.first_name} {emp.user.last_name}!</h3>
                                                <p style="text-align: start; padding-left:60px; margin-bottom:0;">Your Group Passwrod is: </p>
                                                <h2 style="border: 1px dashed #454545 ; display: inline-block; padding: 10px 20px;margin-bottom: 0;">{emp.designation.code}</h2>
                                                <p style="text-align: start; padding-left:60px;">Please save the passcode to perform your activies.</p>
                                            </div>
                                            <br>
                                            <small style="color: #b7b7b7; font-size: x-small;">sent by Oil and Natural Gas Corporation</small><br>
                                            <small style="color: #b7b7b7; font-size: x-small;">No. 5A- 5B, Nelson Mandela Road, Vasant Kunj, New Delhi, 110070</small>
                                        </div>
                                    </div>
                                </center>
                            '''

            from_mail = DEFAULT_FROM_EMAIL
            to_mail = [emp.user.email]

            msg = EmailMultiAlternatives(subject, text_content, from_mail, to_mail)
            msg.attach_alternative(html_content, "text/html")

            if msg.send():
                emp.is_verified = True
                emp.save()

                user = User.objects.get(username=emp.user.username)
                
                group = Group.objects.get(name='employee')
                user.groups.add(group) 
                user.save()

                context = {
                    "modalscript": modalscript,
                    "messageclass": "success",
                    "messageheader": "You are Verified!",
                    "message": "You are account has been successfully verified. Please Login using your username and password!",
                    "primarymessage": "We have sent an email with Group Password. Please check your inbox and save your password for further communication! "
                }
                return render(request, "manager/index.html", context)
        else:
            context = {
                "modalscript": modalscript,
                "messageclass": "danger",
                "messageheader": "OOPS!",
                "message": "Something went wrong. Please try again after sometimes!",
            }
            return render(request, "manager/index.html", context)
    except Exception as e:
        # print(e)
        return redirect('/')

@unauthenticated_user
def loginPage(request):
    
    modalscript =   '''
                    <script>
                        $(document).ready(function(){
                            $('#employee-login').modal('show');
                        })
                    </script>
                    '''

    if request.method == "POST":
        
        if 'signinemployee' in request.POST:
            # Attempt to sign user in
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                if user.type == 'Emp':
                    login(request, user)
                    return redirect('employeedashboard')
                
                else:
                    context = {
                    "modalscript": modalscript,
                    "messageclass": "danger",
                    "messageheader": "Invalid Credentials!",
                    "message": "Please verify your username and password and try again!!",
                    }
                    return render(request, "manager/index.html", context)

            else:
                context = {
                    "modalscript": modalscript,
                    "messageclass": "danger",
                    "messageheader": "Invalid Credentials!",
                    "message": "Please verify your username and password and try again!!",
                }
                return render(request, "manager/index.html", context)
    
        if 'resetemployee' in request.POST:
            forgotuser =  request.POST.get("forgotuser")
            forgotemail =  request.POST.get("forgotemail")
            
            modalscript =   '''
                            <script>
                                $(document).ready(function(){
                                    $('#forgot-password1').modal('show');
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
                                                <a href="http://127.0.0.1:8000/Employee/Reset-Password/{token}" style="font-weight:500; text-decoration: none; color: whitesmoke; background: #198754; padding: 10px 30px; margin-left: 20px; border-radius: 6px;" onMouseOver="this.style.backgroundColor='#116d43'"
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

                msg = EmailMultiAlternatives(subject, text_content, from_mail, to_mail)
                msg.attach_alternative(html_content, "text/html")

                if msg.send():
                    context = {
                        "modalscript": modalscript,
                        "message1": True,
                    }
                    return render(request, "manager/index.html", context)
                
                else:
                    context = {
                        "modalscript": modalscript,
                        "message1": True,
                    }
                    return render(request, "manager/index.html", context)

            except Exception:
                context = {
                    "modalscript": modalscript,
                    "message1": True, 
                }
                return render(request, "manager/index.html", context)
                  
    else:
        context = {
                "modalscript": modalscript,
            }
        return render(request, "manager/index.html", context)

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return render(request, "manager/index.html")

@unauthenticated_user
def reset(request, auth_token):
    modalscript =   '''
                    <script>
                        $(document).ready(function(){
                            $('#forgot-password1').modal('show');
                        })
                    </script>
                    '''

    if request.method == "POST":
        resetpassword = request.POST['resetpassword']
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


@login_required(login_url='login')
@employee_only
def change(request, change):
    change = change
    
    if request.method =="POST":
        if 'Change-Username' in request.POST:
            modal = '''
                    <script>
                        $(document).ready(function(){
                            $('#change-user-name').modal('show');
                        })
                    </script>
                    '''
            username = request.POST['currentusername']
            newuser = request.POST['changeusername']

            try:
                user = User.objects.get(username=username)
                
                if User.objects.filter(username=newuser).first():
                    context = {
                        "modalemployee" : modal,
                        "messageclass": "danger",
                        "messageheader": "Username is already Exists",
                        "message": "Account Creation was unsuccessful. Please Enter different username",
                    }
                    return render(request, "employee/employee-dashboard.html", context)
                
                user.username = newuser
                user.save()

                '''
                context = {
                    "modalemployee" : modal,
                    "messageclass": "success",
                    "messageheader": "Username Changed",
                    "message": "Your username has been changed",
                }
                return render(request, "employee/employee-dashboard.html", context)
                '''
                return redirect('employeedashboard')
            except Exception:
                context = {
                    "modalemployee" : modal,
                    "messageclass": "danger",
                    "messageheader": "OOPS",
                    "message": "Something went wrong! Please check your username!",
                }
                return render(request, "employee/employee-dashboard.html", context)
        
        if 'changepassword' in request.POST:
            modal = '''
                    <script>
                        $(document).ready(function(){
                            $('#change-password').modal('show');
                        })
                    </script>
                    '''
            cpassword = request.POST['cpassword']
            npassword = request.POST['npassword']

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
                            "modalemployee" : modal,
                            "messageclass1": "success",
                            "messageheader1": "Password Changed",
                            "message1": "Your Password has been changed",
                        }
                        return render(request, "employee/employee-dashboard.html", context)
                        '''
                        return redirect('employeedashboard')
                    else:
                        context = {
                        "modalemployee" : modal,
                        "messageclass1": "danger",
                        "messageheader1": "OOPS",
                        "message1": "Your current Password is wrong!",
                    }
                    return render(request, "employee/employee-dashboard.html", context)
                else:
                    return redirect('/')

            except Exception:
                context = {
                    "modalemployee" : modal,
                    "messageclass1": "danger",
                    "messageheader1": "OOPS",
                    "message1": "Something went wrong! Please check your username!",
                }
                return render(request, "employee/employee-dashboard.html", context)
    else:
        if request.user.is_authenticated:
            if change == 'Change-Username':
                modal =   '''
                                <script>
                                    $(document).ready(function(){
                                        $('#change-user-name').modal('show');
                                    })
                                </script>
                                '''
                context = {
                        "modalemployee" : modal,
                }
                return render(request, "employee/employee-dashboard.html", context)
            
            if change == 'Change-Password':
                modal =   '''
                                <script>
                                    $(document).ready(function(){
                                        $('#change-password').modal('show');
                                    })
                                </script>
                                '''
                context = {
                        "modalemployee" : modal,
                }
                return render(request, "employee/employee-dashboard.html", context)
        else:
            return redirect('/')


@login_required(login_url='login')
@employee_only
def employeedashboard(request): 
    if request.user.is_authenticated:
        try:
            user = User.objects.get(username=request.user.username) # Employee User
            emp = Employee.objects.get(user=user) # Employee id
    
            works = WorksOn.objects.only('projectid').filter(empid=emp).filter(Q(status='In Progress') | Q(status='Completed')).order_by('-id') 
            #for pending Projects
            pending = Project.objects.filter(forwardto__contains=emp.designation.name).exclude(project__in=works).order_by('-id')

            #for other Projects
            other = Project.objects.exclude(forwardto__contains=emp.designation.name).all().order_by('-id')

            # all Query of not pending project work
            work = WorksOn.objects.only('projectid').filter(empid=emp).filter(Q(status='Pending') | Q(status='In Progress') | Q(status='Completed')) 
            newone = Project.objects.filter(forwardto__contains=emp.designation.name).exclude(project__in=work)
            for i in range(len(newone)):
                try:
                    work = WorksOn.objects.create(empid=emp, projectid=newone[i], status="Pending")
                    work.save()
                except Exception:
                    pass

            if request.method == "POST":
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
                    'modalemployee' : modal,
                    'pending' : pending,
                    'past' : works,
                    'other' : other,
                    'pendingactive': True
                }

                if not myuploadfile=='':
                    check_image = imghdr.what(myuploadfile)
                    if not (check_image== "jpg" or check_image== "jpeg" or check_image== "png"):
                        return render(request, "employee/employee-dashboard.html", context)
                    else:
                        try:
                            old_file = emp.image
                            if not old_file.name == myuploadfile:
                                if os.path.isfile(old_file.path):
                                    os.remove(old_file.path)
                        except Exception:
                            pass
                        emp.image = myuploadfile
                        emp.save()
                        return render(request, "employee/employee-dashboard.html", context)

                
            
            context = {
                'pending' : pending,
                'past' : works,
                'other' : other,
                'pendingactive': True
            }
            return render(request, "employee/employee-dashboard.html", context)

        except Exception:
            pass


@login_required(login_url='login')
@employee_only
def keymodal(request, title, id):
    title = title.replace("%20", " ")
    try:
        checkgetitem = Project.objects.filter(title=title).filter(id=id).first()
        if checkgetitem:
            if request.user.is_authenticated:
                user = User.objects.get(username=request.user.username) # Employee User
                emp = Employee.objects.get(user=user) # Employee id
        
                works = WorksOn.objects.only('projectid').filter(empid=emp).filter(Q(status='In Progress') | Q(status='Completed')).order_by('-id') 
                #for pending Projects
                pending = Project.objects.filter(forwardto__contains=emp.designation.name).exclude(project__in=works).order_by('-id')

                #for other Projects
                other = Project.objects.exclude(forwardto__contains=emp.designation.name).all().order_by('-id')

                id = id
                title = title

                checkid = pending.filter(id=id).all()

                if checkid:
                    context = {
                        "modal" : True,
                        "id" : id,
                        "title" : title,
                        'pending' : pending,
                        'past' : works,
                        'other' : other,
                        'pendingactive': True
                    }
                else:
                    context = {
                        "modal" : True,
                        "id" : id,
                        "title" : title,
                        'pending' : pending,
                        'past' : works,
                        'other' : other,
                        'otheractive': True
                    }
                    
                return render(request, "employee/employee-dashboard.html", context)
        else:
            raise Http404("URL Does not Exist")
    except Exception:
        raise Http404("URL does not Exist")

@login_required(login_url='login')
@employee_only
def download(request, title, id):
    title = title.replace("%20", " ")
    try:
        checkgetitem = Project.objects.filter(title=title).filter(id=id).first()
        if checkgetitem:
            if request.method == "POST":
                key = request.POST.get('decryptionkey')
                
                try:
                    project = Project.objects.get(id=id)                
                    file = project.projectfile
                    filename = project.projectfile.url
                    filename = filename.replace('/', '\\')

                    ROOT_DIR = dirname(dirname(__file__))
                    fullpath=str(ROOT_DIR) + str(filename) 
                    
                    try:
                        enc = Encryptor(key)
                        dec =enc.decrypt_file(fullpath)
                    
                        fs = FileSystemStorage()
                        file = os.path.basename(fullpath)
                        file = file[:-4]
                        if fs.exists(file):
                            with fs.open(file) as pdf:
                                response = HttpResponse(pdf, content_type='vnd.ms-word')
                                response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file)
                                fs.delete(file)
                                
                                try:
                                    if request.user.is_authenticated:
                                        username= request.user.username
                                        user = User.objects.get(username=username)
                                        emp = Employee.objects.get(user=user)
                                        works = WorksOn.objects.get(empid=emp, projectid=project)
                                        works.status = "In Progress"
                                        works.save()
                                except Exception:
                                    pass
                                
                                return response
                        else:
                            return HttpResponseNotFound('The requested file was not found in our server.')
                    except Exception as e:
                        if request.user.is_authenticated:
                            user = User.objects.get(username=request.user.username) # Employee User
                            emp = Employee.objects.get(user=user) # Employee id
                    
                            works = WorksOn.objects.only('projectid').filter(empid=emp).filter(Q(status='In Progress') | Q(status='Completed')).order_by('-id') 
                            #for pending Projects
                            pending = Project.objects.filter(forwardto__contains=emp.designation.name).exclude(project__in=works).order_by('-id')

                            #for other Projects
                            other = Project.objects.exclude(forwardto__contains=emp.designation.name).all().order_by('-id')
                            id = id
                            title = title
                            context = {
                                "modal" : True,
                                "id" : id,
                                "title" : title,
                                'pending' : pending,
                                'past' : works,
                                'other' : other,
                                'pendingactive': True,
                                "messageclass": "danger",
                                "messageheader": "Invalid Key!",
                                "message": "Please verify your key and try agian!!",
                            }
                            return render(request, "employee/employee-dashboard.html", context)


                except Exception as e:
                    #print(e)
                    return redirect('employeedashboard')
                    
            else:
                return redirect('employeedashboard')
        else:
            raise Http404("URL Does not Exist")
    except Exception:
        raise Http404("URL does not Exist")
        
@login_required(login_url='login')
@employee_only
def completed(request, id):
    if request.user.is_authenticated:
        username= request.user.username
        user = User.objects.get(username=username)
        emp = Employee.objects.get(user=user)
        works = WorksOn.objects.only('projectid').filter(empid=emp).filter(Q(status='In Progress') | Q(status='Completed')).order_by('-id') 
        #for pending Projects
        pending = Project.objects.filter(forwardto__contains=emp.designation.name).exclude(project__in=works).order_by('-id')

        #for other Projects
        other = Project.objects.exclude(forwardto__contains=emp.designation.name).all().order_by('-id')
    
        if request.method == "POST":
            completed = request.POST.get('completed')

            try:
                project = Project.objects.get(id=id)
                workson = WorksOn.objects.get(empid=emp, projectid=project)

                if not workson.status == "Completed":
                    workson.status = "Completed"
                    workson.save()
                
                context={
                    "projectid" : project.id,
                    'pending' : pending,
                    'past' : works,
                    'other' : other,
                    "pastactive" : True,
                }

                return render(request, "employee/employee-dashboard.html", context)

            except Exception:
                pass
        else:
            return redirect('employeedashboard')

@login_required(login_url='login')
@employee_only
def keyrequest(request, id): 
    if request.user.is_authenticated:
        username= request.user.username
        user = User.objects.get(username=username)
        emp = Employee.objects.get(user=user)
        works = WorksOn.objects.only('projectid').filter(empid=emp).filter(Q(status='In Progress') | Q(status='Completed')).order_by('-id') 
        #for pending Projects
        pending = Project.objects.filter(forwardto__contains=emp.designation.name).exclude(project__in=works).order_by('-id')
        #for other Projects
        other = Project.objects.exclude(forwardto__contains=emp.designation.name).all().order_by('-id')

        try:
            project = Project.objects.get(id=id)
            existcheck = KeyRequest.objects.filter(empid=emp).filter(projectid=project).first()
            projectcheck = Project.objects.filter(forwardto__contains=emp.designation.name).filter(id=id).first()
            if existcheck:
                if projectcheck:
                    context={
                        "modal" : True,
                        "id" : id,
                        "title" : project.title,
                        'pending' : pending,
                        'past' : works,
                        'other' : other,
                        'pendingactive': True,
                        "messageclass": "danger",
                        "messageheader": "OOPS!",
                        "message": "You are already requested! we will get back to you shortly!"
                    }
                    return render(request, "employee/employee-dashboard.html", context)
                else:
                    context={
                        "modal" : True,
                        "id" : id,
                        "title" : project.title,
                        'pending' : pending,
                        'past' : works,
                        'other' : other,
                        'otheractive': True,
                        "messageclass": "danger",
                        "messageheader": "OOPS!",
                        "message": "You are already requested! we will get back to you shortly!"
                    }
                    return render(request, "employee/employee-dashboard.html", context)
            
            if projectcheck:
                requestproject = KeyRequest.objects.create(empid=emp, projectid=project, reason="Missing/New User")
                requestproject.save()

                context={
                    "modal" : True,
                    "id" : id,
                    "title" : project.title,
                    'pending' : pending,
                    'past' : works,
                    'other' : other,
                    'pendingactive': True,
                    "messageclass": "success",
                    "messageheader": "Your request has been raised!",
                    "message": "The request is now on hold until the request has been approved! we will get back to you shortly"
                }
                return render(request, "employee/employee-dashboard.html", context)
            
            else:
                requestproject = KeyRequest.objects.create(empid=emp, projectid=project, reason="for reference")
                requestproject.save()

                context={
                    "modal" : True,
                    "id" : id,
                    "title" : project.title,
                    'pending' : pending,
                    'past' : works,
                    'other' : other,
                    'otheractive': True,
                    "messageclass": "success",
                    "messageheader": "Your request has been raised!",
                    "message": "The request is now on hold until the request has been approved! we will get back to you shortly"
                }
                return render(request, "employee/employee-dashboard.html", context)
        except Exception:
            raise Http404("Does not Exist")
    

@login_required(login_url='login')
@employee_only
def transportation(request):
    if request.user.is_authenticated:
        username= request.user.username
        user = User.objects.get(username=username)
        employeename= user.first_name + " " + user.last_name
        emp = Employee.objects.get(user=user)
        project = Project.objects.filter(forwardto__contains=emp.designation.name).all().order_by('-id')
        alltransportation = Transportation.objects.filter(employee=employeename).all().order_by('-id')

        p = Paginator(alltransportation, 5) #10
        page_num = request.GET.get('Page', 1)
        seeall = request.GET.get('View')

        if seeall == 'seeall':
            seeall = True
            page = Transportation.objects.filter(employee=employeename).all().order_by('-id')
        else:
            try:
                page = p.page(page_num)

            except PageNotAnInteger:
                page = p.page(1)
            except EmptyPage:
                page = p.page(p.num_pages)


        if request.method == "POST":
            transportnumber = request.POST.get('tnumber')
            projectname = request.POST.get('pname')
            place = request.POST.get('place')

            try:
                project1 = Project.objects.filter(title=projectname).filter(forwardto__contains=emp.designation.name).all()
                transports = Transportation.objects.filter(project=projectname).filter(employee=employeename).first()

                if transports: 
                    context = {
                        'alltransportation' : page,
                        'seeall' : seeall,
                        'transportlist' : project,
                        "messageclass": "danger",
                        "messageheader": "You are already submitted",
                        "message": "Tranposrtation details for this invoice is already done",
                    }
                    return render(request, "employee/employee-transportation.html", context)
                
                if projectname == 'Nothing...':
                    context = {
                        'alltransportation' : page,
                        'seeall' : seeall,
                        'transportlist' : project,
                        "messageclass": "danger",
                        "messageheader": "Tranportation process is unsuccessfull",
                        "message": "You haven't project yet!",
                    }
                    return render(request, "employee/employee-transportation.html", context)
                if not project1:
                    context = {
                        'alltransportation' : page,
                        'seeall' : seeall,
                        'transportlist' : project,
                        "messageclass": "danger",
                        "messageheader": "Transportation process is unsuccessfull",
                        "message": "The project does not exist!",
                    }
                    return render(request, "employee/employee-transportation.html", context)
                    
            except Project.DoesNotExist:
                context = {
                    'alltransportation' : page,
                    'seeall' : seeall,
                    'transportlist' : project,
                    "messageclass": "danger",
                    "messageheader": "Transportation is unsuccessfull",
                    "message": "The project does not exist!",
                }
                return render(request, "employee/employee-transportation.html", context)
            
            else:
                try:
                    transport = Transportation.objects.create(transportnumber=transportnumber, project=projectname, place=place, employee=employeename)
                    transport.save()
                    
                    context = {
                        'alltransportation' : page,
                        'seeall' : seeall,
                        'transportlist' : project,
                        "messageclass": "success",
                        "messageheader": "Thank you for your Transportation Details",
                        "message": "Your Transportation for this invoice is done",
                    }
                    return render(request, "employee/employee-transportation.html", context)
                except Exception:
                    context = {
                        'alltransportation' : page,
                        'seeall' : seeall,
                        'transportlist' : project,
                        "messageclass": "danger",
                        "messageheader": "OOPS!",
                        "message": "Something went wrong!",
                    }
                    return render(request, "employee/employee-transportation.html", context)

        context = {
            'alltransportation' : page,
            'seeall' : seeall,
            'transportlist' : project,
        }

        return render(request, "employee/employee-transportation.html", context)

@login_required(login_url='login')
@employee_only
def payment(request):
    if request.user.is_authenticated:
        username= request.user.username
        user = User.objects.get(username=username)
        employeename= user.first_name + " " + user.last_name
        emp = Employee.objects.get(user=user)
        project = Project.objects.filter(forwardto__contains=emp.designation.name).all().order_by('-id')
        allpayment = Payment.objects.filter(employee=employeename).all().order_by('-id')
        totalamount = Payment.objects.filter(employee=employeename).aggregate(sum=Sum('amount'))

        p = Paginator(allpayment, 5) #10
        page_num = request.GET.get('Page', 1)
        seeall = request.GET.get('View')

        if seeall == 'seeall':
            seeall = True
            page = Payment.objects.filter(employee=employeename).all().order_by('-id')
        else:
            try:
                page = p.page(page_num)

            except PageNotAnInteger:
                page = p.page(1)
            except EmptyPage:
                page = p.page(p.num_pages)


        if request.method == "POST":
            projectname = request.POST.get('pname')
            place = request.POST.get('place')
            amount = request.POST.get('payment')

            try:
                project1 = Project.objects.filter(title=projectname).filter(forwardto__contains=emp.designation.name).all()
                payments = Payment.objects.filter(project=projectname).filter(employee=employeename).first()

                if payments: 
                    context = {
                        'totalamount' : totalamount["sum"],
                        'allpayment' : page,
                        'seeall' : seeall,
                        'paymentlist' : project,
                        "messageclass": "danger",
                        "messageheader": "You are already Paid",
                        "message": "Payment for this invoice is already done",
                    }
                    return render(request, "employee/employee-payment.html", context)
                
                if projectname == 'Nothing...':
                    context = {
                        'totalamount' : totalamount["sum"],
                        'allpayment' : page,
                        'seeall' : seeall,
                        'paymentlist' : project,
                        "messageclass": "danger",
                        "messageheader": "Payment is unsuccessfull",
                        "message": "You haven't project yet!",
                    }
                    return render(request, "employee/employee-payment.html", context)
                if not project1:
                    context = {
                        'totalamount' : totalamount["sum"],
                        'allpayment' : page,
                        'seeall' : seeall,
                        'paymentlist' : project,
                        "messageclass": "danger",
                        "messageheader": "Payment is unsuccessfull",
                        "message": "The project does not exist!",
                    }
                    return render(request, "employee/employee-payment.html", context)
                    
            except Project.DoesNotExist:
                context = {
                    'totalamount' : totalamount["sum"],
                    'allpayment' : page,
                    'seeall' : seeall,
                    'paymentlist' : project,
                    "messageclass": "danger",
                    "messageheader": "Payment is unsuccessfull",
                    "message": "The project does not exist!",
                }
                return render(request, "employee/employee-payment.html", context)
            
            else:
                try:
                    payment = Payment.objects.create(project=projectname, projectplace=place, employee=employeename, amount=amount)
                    payment.save()
                    
                    context = {
                        'totalamount' : totalamount["sum"],
                        'allpayment' : page,
                        'seeall' : seeall,
                        'paymentlist' : project,
                        "messageclass": "success",
                        "messageheader": "Thank you for your payment",
                        "message": "Payment for this invoice is done",
                    }
                    return render(request, "employee/employee-payment.html", context)
                except Exception:
                    context = {
                        'totalamount' : totalamount["sum"],
                        'allpayment' : page,
                        'seeall' : seeall,
                        'paymentlist' : project,
                        "messageclass": "danger",
                        "messageheader": "OOPS!",
                        "message": "Something went wrong!",
                    }
                    return render(request, "employee/employee-payment.html", context)

        context = {
            'totalamount' : totalamount["sum"],
            'allpayment' : page,
            'seeall' : seeall,
            'paymentlist' : project
        }

        return render(request, "employee/employee-payment.html", context)


@login_required(login_url='login')
@employee_only
def invoice(request, title, id):
    title = title.replace("%20", " ")
    if request.user.is_authenticated:
        username= request.user.username
        user = User.objects.get(username=username)
        employeename= user.first_name + " " + user.last_name
        emp = Employee.objects.get(user=user)
        designation = emp.designation.name
        
        if title == 'Payment':
            payment = get_object_or_404(Payment, id=id)

            if payment.employee == employeename:
                
                data = {
                    'invoice' : payment,
                    'designation' : designation,
                    'email' : user.email,
                    'paymentinvoice' : True,
                }
                pdf = render_to_pdf('employee/invoicepdf.html', data)
                return HttpResponse(pdf, content_type='application/pdf')
            
            else:
                return redirect('payment')
        
        elif title == "Transportation":
            transport = get_object_or_404(Transportation, id=id)

            if transport.employee == employeename:
                data = {
                    'invoice' : transport,
                    'designation' : designation,
                    'email' : user.email,
                    'paymentinvoice' : False,
                }
                pdf = render_to_pdf('employee/invoicepdf.html', data)
                return HttpResponse(pdf, content_type='application/pdf')
            
            else:
                return redirect('transportation')
        
        else:
            return redirect("employeedashboard")


@login_required(login_url='login')
@employee_only
def downloadinvoice(request, title, id):
    title = title.replace("%20", " ")
    if request.user.is_authenticated:
        username= request.user.username
        user = User.objects.get(username=username)
        employeename= user.first_name + " " + user.last_name
        emp = Employee.objects.get(user=user)
        designation = emp.designation.name
        
        if title == 'Payment':
            payment = get_object_or_404(Payment, id=id)

            if payment.employee == employeename:
                
                data = {
                    'invoice' : payment,
                    'designation' : designation,
                    'email' : user.email,
                    'paymentinvoice' : True,
                }
                pdf = render_to_pdf('employee/invoicepdf.html', data)
                
                response = HttpResponse(pdf, content_type='application/pdf')
                file = "Invoice_"+employeename+"_Payment_"+str(payment.id)+".pdf"
                content = 'attachment; filename=%s' % smart_str(file)
                response['Content-Disposition'] = content
                return response
            
            else:
                return redirect('payment')
        
        elif title == "Transportation":
            transport = get_object_or_404(Transportation, id=id)

            if transport.employee == employeename:
                data = {
                    'invoice' : transport,
                    'designation' : designation,
                    'email' : user.email,
                    'paymentinvoice' : False,
                }
                pdf = render_to_pdf('employee/invoicepdf.html', data)
                
                response = HttpResponse(pdf, content_type='application/pdf')
                file = "Invoice_"+employeename+"_Transport_"+str(transport.id)+".pdf"
                content = 'attachment; filename=%s' % smart_str(file)
                response['Content-Disposition'] = content
                return response
            
            else:
                return redirect('transportation')
        
        else:
            return redirect("employeedashboard")