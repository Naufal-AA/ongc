from django.urls import path, re_path
from . import views

urlpatterns = [
    path("Managing-Director/Login", views.loginmanager, name="loginmanager"),
    path("Managing-Director/Reset-Password/<auth_token>", views.resetmanager, name="resetmanager"),
    path("Managing-Director/Dashboard", views.dashboard, name="dashboard"),
    path("Managing-Director/Notification", views.notification, name="notification"),
    path("Managing-Director/AddProjects", views.addproject, name="addproject"),
    path("Managing-Director/ViewProjects", views.viewproject, name="viewproject"),
    path("Managing-Director/viewEmployee", views.viewemployee, name="viewemployee"),
    path("Managing-Director/ViewDepartment", views.viewdepartment, name="viewdepartment"),
    path("Managing-Director/ViewRequest", views.viewrequest, name="viewrequest"),
    path("Managing-Director/Logout", views.logoutmanager, name="logoutmanager"),
    path("Managing-Director/<change>", views.changemanager, name="changemanager"),
    path("Managing-Director/View-Request/<int:id>/<str:permit>", views.keypermit, name="keypermit"),
    path("Managing-Director/Edit-Project/<str:title>/<int:id>", views.editproject, name="editproject"),
    path("Managing-Director", views.searchmanager, name="searchmanager"),   
]