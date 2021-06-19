from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("Employee/Register", views.register, name="register"),
    path("Employee/Login", views.loginPage, name="login"),
    path('Employee/verify/<auth_token>', views.verify, name="verify"),
    path('Employee/Reset-Password/<auth_token>', views.reset, name="reset"),
    path("Employee/Dashboard", views.employeedashboard, name="employeedashboard"),
    path("Employee/Dashboard/<str:title>/<int:id>", views.keymodal, name="keymodal"),
    path("Employee/Dashboard/Download/<str:title>/<int:id>", views.download, name="download"),
    path("Employee/Transportation", views.transportation, name="transportation"),
    path("Employee/Payment", views.payment, name="payment"),
    path("Employee/Logout", views.logout_view, name="logout"),
    path("Employee/<change>", views.change, name="change"),
    path("Employee/Request/<int:id>", views.completed, name="completed"),
    path("Employee/Key-Request/<int:id>", views.keyrequest, name="keyrequest"),
    path("Employee/Invoice-Details/<title>/<int:id>", views.invoice, name="invoice"),
    path("Employee/Download-Invoice/<title>/<int:id>", views.downloadinvoice, name="downloadinvoice"),
]