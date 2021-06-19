from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
	def wrapper_func(request, *args, **kwargs):
		if request.user.is_authenticated:
			type = request.user.type
			
			if type == 'Emp':
				return redirect('employeedashboard')
			elif type == 'MAN':
				return redirect('dashboard')
			elif type == 'ADM':
				return redirect('admindashboard')  
			else:
				return redirect('index')  
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func


def employee_only(view_func):
	def wrapper_function(request, *args, **kwargs):
		group = None
		if request.user.groups.exists():
			group = request.user.groups.all()[0].name

		if not group == 'employee':
			return redirect('index')

		if group == 'employee':
			return view_func(request, *args, **kwargs)

	return wrapper_function

def manager_only(view_func):
	def wrapper_function(request, *args, **kwargs):
		group = None
		if request.user.groups.exists():
			group = request.user.groups.all()[0].name

		if not group == 'manager':
			return redirect('index')

		if group == 'manager':
			return view_func(request, *args, **kwargs)

	return wrapper_function

def admin_only(view_func):
	def wrapper_function(request, *args, **kwargs):
		group = None
		if request.user.groups.exists():
			group = request.user.groups.all()[0].name

		if not group == 'admin':
			return redirect('index')

		if group == 'admin':
			return view_func(request, *args, **kwargs)

	return wrapper_function