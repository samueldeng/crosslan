from django.shortcuts import render, render_to_response, get_object_or_404
from django.contrib import auth
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from crosslan import models
import json

# Create your views here.
def index(request):
	return render(request, 'crosslan/index.html')

def register(request):
	c = {}
	c.update(csrf(request))
	return render_to_response('crosslan/register.html', c)

def login(request):
	status = 0
	if (request.POST.has_key('password')):
		username = request.POST['username']
		password = request.POST['password']
		user = auth.authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				auth.login(request, user)
				status = 0
			else:
				status = 2
		else:
			status = 1
	elif (request.user.is_authenticated()):
		return HttpResponseRedirect(reverse('crosslan:index'))
	else:
		c = {}
		c.update(csrf(request))
		return render_to_response('crosslan/login.html', c)
	return HttpResponse(json.dumps({'status':status}), content_type="text/plain")

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect(reverse('crosslan:index'))

def info(request):
	return render(request, 'crosslan/index.html')
