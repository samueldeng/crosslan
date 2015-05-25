from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect
from django.db import IntegrityError

from crosslan import models, utils, backend, conf
import json, traceback

# Create your views here.
def index(request):
	return render(request, 'crosslan/index.html')

def signup(request):
	try:
		if (request.user.is_authenticated()):
			return HttpResponseRedirect(reverse('crosslan:info'))
		elif (request.method == "POST"):
			try:
				username = request.POST['username']
				password = request.POST['password']
				email    = request.POST['email']
				redeem   = request.POST['redeem']
			except:
				return HttpResponse(json.dumps({'status':1}), content_type="text/plain")
			if (username=='' or password=='' or email=='' or redeem==''):
				return HttpResponse(json.dumps({'status':1}), content_type="text/plain")
			elif (auth.models.User.objects.filter(username=username).exists()):
				return HttpResponse(json.dumps({'status':2}), content_type="text/plain")
			elif (not models.RedeemCode.objects.filter(code=redeem,status=models.RedeemCode.ACTIVE).exists()):
				# Add Current-IP
				return HttpResponse(json.dumps({'status':3}), content_type="text/plain")
			else:
				code = models.RedeemCode.objects.get(code=redeem)
				if (code.status == models.RedeemCode.INACTIVE):
					return HttpResponse(json.dumps({'status':3}), content_type="text/plain")
				elif (code.status == models.RedeemCode.USED):
					return HttpResponse(json.dumps({'status':4}), content_type="text/plain")
				else:
					if(not code.use()):
						return HttpResponse(json.dumps({'status':4}), content_type="text/plain")
					code.save()
					try:
						user = User.objects.create_user(username=username, email=email, password=password)
						user.save()
					except Exception:
						code.recycle()
						code.save()
						return HttpResponse(json.dumps({'status':2}), content_type="text/plain")
					port = utils.getNextPort()
					if(port<0):
						# Port Range Full
						return HttpResponse(json.dumps({'status':5}), content_type="text/plain")
					clUser = models.CrossLanUser.objects.create_user(user=user, host=conf.PROXY_HOST, port = port);
					clUser.save()
					retry = 0
					r = backend.newUser(port)
					while (r is not True and retry < conf.RETRIES):
						r = backend.newUser(port)
						retry = retry + 1
					if(retry == conf.RETRIES):
						# Check Backend Server
						return HttpResponse(json.dumps({'status':6}), content_type="text/plain")
					retry = 0
					r = backend.startProxy(port)
					while (r is not True and retry < conf.RETRIES):
						r = backend.newUser(port)
						retry = retry + 1
					return HttpResponse(json.dumps({'status':0, 'redirect':reverse('crosslan:signin')}), content_type="text/plain")
		else:
			c = {}
			c.update(csrf(request))
			return render(request, 'crosslan/signup.html', c)
	except Exception,e:
		print traceback.format_exc()

def signin(request):
	status = 0
	redirect = ""
	if ('username' in request.POST and 'password' in request.POST):
		username = request.POST['username']
		password = request.POST['password']
		user = auth.authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				auth.login(request, user)
				status = 0
				redirect = reverse('crosslan:info')
			else:
				status = 2
		else:
			status = 1
	elif (request.user.is_authenticated()):
		return HttpResponseRedirect(reverse('crosslan:info'))
	else:
		c = {}
		c.update(csrf(request))
		c.update({'signout':utils.SIGNAL_SIGNOUT})
		if (utils.SIGNAL_SIGNOUT):
			utils.SIGNAL_SIGNOUT = False
		return render(request, 'crosslan/signin.html', c)
	return HttpResponse(json.dumps({'status':status, 'redirect':redirect}), content_type="text/plain")

def signout(request):
	if (request.user.is_authenticated()):
		auth.logout(request)
	utils.SIGNAL_SIGNOUT = True
	return HttpResponseRedirect(reverse('crosslan:signin'))

# Fuck Python Circular Import
from django.contrib.auth.decorators import login_required
@login_required(login_url=reverse_lazy('crosslan:signin'))
def info(request):
	u = request.user.crosslanuser
	pachost = conf.PAC_HOST + ':' + str(u.port) + '/pac'
	host = u.host + ':' + str(u.port)
	try:
		status = backend.getProxyStatus(u.port)
	except Exception:
		print traceback.format_exc()
		status = False
	if(status is False):
		status = 'Unknown'
	balance = utils.getHuman(u.data)
	bind = u.bind
	clientIp = utils.getClientIp(request)
	ipObjects = models.BindingIP.objects.exclude(user=u, ip=clientIp).filter(user=u)
	ips = []
	for ipOb in ipObjects:
		ips.append(ipOb.ip)
	if(clientIp not in ips):
		newIp = models.BindingIP.objects.bind_ip(user=u, ip=clientIp)
		newIp.save()
		backend.setBindIp(u.port,ips)
	c = {
		 'pachost': pachost,
		 'host': host,
		 'status': status,
		 'balance': balance,
		 'bind': bind,
		 'clientIp': clientIp,
		 'ips': ips,
		}
	c.update(csrf(request))
	return render(request, 'crosslan/info.html', c)

@login_required(login_url=reverse_lazy('crosslan:signin'))
def refreshInfo(request):
	#TODO: What if User visit /info/refresh directly
	u = request.user.crosslanuser
	host = u.host + ':' + str(u.port)
	try:
		backend.restartProxy(u.port)
		status = backend.getProxyStatus(u.port)
	except Exception:
		print traceback.format_exc()
		status = False
	if(status is False):
		status = 'Unknown'
	deltaData = backend.getDataUsage(u.port)
	u.data = u.data + deltaData
	u.save()
	balance = utils.getHuman(u.data)
	c = {
		 'host': host,
		 'status': status,
		 'balance': balance,
		}
	return HttpResponse(json.dumps(c), content_type="text/plain")

@login_required(login_url=reverse_lazy('crosslan:signin'))
def rebindIp(request):
	try:
		if(request.method == "POST"):
			u = request.user.crosslanuser
			if(request.POST['bind'] == "false"):
				u.bind = False
			elif(request.POST['bind'] == "true"):
				u.bind = True
			else:
				return HttpResponse(json.dumps({"message":"Bind Error"}), content_type="text/plain")
			u.save()
			models.BindingIP.objects.filter(user=u).delete()
			ips = request.POST['ips'].split(",")
			ips = utils.unique(ips)
			for ip in ips:
				i = models.BindingIP.objects.bind_ip(user=u, ip=ip)
				i.save()
			backend.setBindIp(u.port, ips)
			return HttpResponse(json.dumps({"message":"Good"}), content_type="text/plain")
		else:
			return HttpResponse(json.dumps({"message":"Bad"}), content_type="text/plain")
	except Exception, e:
		print e.message
		traceback.format_exc()
		return HttpResponse(json.dumps({"message":"Error"}), content_type="text/plain")

