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
			port = utils.getNextPort()
			if(port<0):
				# Port Range Full
				return HttpResponse(json.dumps({'status':5}), content_type="text/plain")
			if (auth.models.User.objects.filter(username=username).exists()):
				user = User.objects.get(username=username)
				if(models.CrossLanUser.objects.filter(user=user).exists()):
					return HttpResponse(json.dumps({'status':2}), content_type="text/plain")
				else:
					user = auth.authenticate(username=username, password=password)
					if (user is not None and user.is_active):
						clUser = models.CrossLanUser.objects.create_user(user=user, host=conf.PROXY_HOST, port = port);
						clUser.save()
						retry = 0
						r = backend.newUser(port)
						while (not r and retry < conf.RETRIES):
							r = backend.newUser(port)
							retry = retry + 1
						if(retry == conf.RETRIES):
							clUser.delete()
							return HttpResponse(json.dumps({'status':6}), content_type="text/plain")
						backend.startProxy(port)
						return HttpResponse(json.dumps({'status':0, 'redirect':reverse('crosslan:signin')}), content_type="text/plain")
					else:
						return HttpResponse(json.dumps({'status':2}), content_type="text/plain")
			if (not models.RedeemCode.objects.filter(code=redeem).exists()):
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
					clUser = models.CrossLanUser.objects.create_user(user=user, host=conf.PROXY_HOST, port = port);
					clUser.save()
					retry = 0
					r = backend.newUser(port)
					while (not r and retry < conf.RETRIES):
						r = backend.newUser(port)
						retry = retry + 1
					if(retry == conf.RETRIES):
						code.recycle()
						user.delete()
						return HttpResponse(json.dumps({'status':6}), content_type="text/plain")
					backend.startProxy(port)
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
from django.contrib.auth.decorators import login_required, user_passes_test
@login_required(login_url=reverse_lazy('crosslan:signin'))
def info(request):
	try:
		u = request.user.crosslanuser
	except:
		print traceback.format_exc()
		return signout()
	pachost = conf.PAC_HOST + ':' + str(u.port) + '/pac'
	host = u.host + ':' + str(u.port)
	status = backend.getProxyStatus(u.port)
	balance = utils.getHuman(u.data)
	bind = u.bind
	clientIp = utils.getClientIp(request)
	ipObjects = models.BindingIP.objects.filter(user=u)
	ips = []
	for ipOb in ipObjects:
		ips.append(ipOb.ip)
	if(clientIp not in ips):
		newIp = models.BindingIP.objects.bind_ip(user=u, ip=clientIp)
		newIp.save()
		backend.setBindIp(u.port,ips)
	if (clientIp in ips):
		ips.remove(clientIp)
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
	if(backend.updateData(user=u) is False):
		balance = 'Unknown'
	else:
		balance = utils.getHuman(u.data)
	status = backend.getProxyStatus(u.port)
	if (status is not 'Running' and u.data > 0):
		backend.startProxy(u.port)
		status = backend.getProxyStatus(u.port)
	c = {
		 'host': host,
		 'status': status,
		 'balance': balance,
		}
	return HttpResponse(json.dumps(c), content_type="text/plain")

@login_required(login_url=reverse_lazy('crosslan:signin'))
def switchProxy(request):
	try:
		if(request.method == "POST"):
			u = request.user.crosslanuser
			proxyStatus = backend.getProxyStatus(u.port)
			action = request.POST['action']
			if(proxyStatus == 'Running' or action == 'stop'):
				backend.stopProxy(u.port)
				return HttpResponse(json.dumps({"status":backend.getProxyStatus(u.port), "code":0}), content_type="text/plain")
			elif(proxyStatus == 'Stopped' or action == 'start'):
				if(u.data <= 0 or backend.updateData(u) < 0):
					return HttpResponse(json.dumps({"status":backend.getProxyStatus(u.port), "code":2}), content_type="text/plain")
				backend.startProxy(u.port)
				return HttpResponse(json.dumps({"status":backend.getProxyStatus(u.port), "code":0}), content_type="text/plain")
			else:
				return HttpResponse(json.dumps({"status":proxyStatus, "code":1}), content_type="text/plain")
	except:
		print traceback.format_exc()
		return HttpResponse(json.dumps({"status":backend.getProxyStatus(u.port), "code":3}), content_type="text/plain")

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
			ips = request.POST['ips'].split(",")
			ips = utils.unique(ips)
			existsIpObjects = models.BindingIP.objects.filter(user=u)
			existsIps = []
			ipToRemove = []
			for eIpOb in existsIpObjects:
				existsIps.append(eIpOb.ip)
				if(eIpOb.ip not in ips):
					ipToRemove.append(eIpOb.ip)
			for ip in ipToRemove:
				models.BindingIP.objects.filter(user=u,ip=ip).delete()
			for ip in ips:
				if(ip not in existsIps):
					i = models.BindingIP.objects.bind_ip(user=u, ip=ip)
					i.save()
			if(not u.bind):
				ips = []
			backend.setBindIp(u.port,ips)
			return HttpResponse(json.dumps({"message":"Good"}), content_type="text/plain")
		else:
			return HttpResponse(json.dumps({"message":"Bad"}), content_type="text/plain")
	except Exception, e:
		print traceback.format_exc()
		return HttpResponse(json.dumps({"message":"Error"}), content_type="text/plain")

@user_passes_test(lambda u: u.is_superuser, login_url=reverse_lazy('crosslan:signin'))
def adminControlPanel(request):
	#TODO: Build a convinient Control Panel for Administrator
	return HttpResponse(json.dumps({"message":"Good"}), content_type="text/plain")
