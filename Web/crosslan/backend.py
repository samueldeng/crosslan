from crosslan import conf, models, utils
import requests, json, traceback

from django_cron import CronJobBase, Schedule, CronJobLog

class RequestsError:
	status_code = 800

def Post(url, data):
	try:
		r = requests.post(conf.BACKEND_HOST + url, json.dumps(data))
		return r
	except Exception, e:
		print traceback.format_exc()
		return RequestsError()

def Put(url, data):
	try:
		r = requests.put(conf.BACKEND_HOST + url, json.dumps(data))
		return r
	except Exception, e:
		print traceback.format_exc()
		return RequestsError()

def Get(url):
	try:
		r = requests.get(conf.BACKEND_HOST + url)
		return r
	except Exception, e:
		print traceback.format_exc()
		return RequestsError()

def operateProxy(port, action):
	url = str(port) + '/running-status'
	data = {'action':action}
	r = Put(url, data)
	if(r.status_code == 201):
		return True
	elif(r.status_code == 800):
		print '[FAILED]Backend.operateProxy(): RequestsError\n'
		return False
	else:
		print '[FAILED]Backend.operateProxy():\n' \
			+ '\tUrl: %s\n' %url \
			+ '\tAction: %s\n' %action \
			+ '\tStatus Code: %s\n' %r.status_code \
			+ '\tJSON: %s\n' %utils.getMsgOrFalse(r)
		return False

# Here Begins Functions Communicate with Backend
def newUser(port):
	url = str(port)
	data = {}
	r = Post(url, data)
	if(r.status_code == 201):
		return True
	elif(r.status_code == 800):
		print '[FAILED]Backend.newUser(): RequestsError\n'
		return False
	else:
		print '[FAILED]Backend.newUser():\n' \
			+ '\tUrl: %s\n' %url \
			+ '\tStatus Code: %s\n' %r.status_code \
			+ '\tJSON: %s\n' %utils.getMsgOrFalse(r)
		return False

def startProxy(port):
	return operateProxy(port, 'start')

def stopProxy(port):
	return operateProxy(port, 'stop')

def restartProxy(port):
	return operateProxy(port, 'restart')

def getProxyStatus(port):
	url = str(port) + '/running-status'
	r = Get(url)
	if(r.status_code == 201):
		if(r.json()['status'] == 'running'):
			return 'Running'
		else:
			return 'Stopped'
	elif(r.status_code == 800):
		print '[FAILED]Backend.getProxyStatus(): RequestsError\n'
		return 'Unknown'
	else:
		print '[FAILED]Backend.getProxyStatus():\n'  \
			+ '\tUrl: %s\n'  %url \
			+ '\tStatus Code: %s\n' %r.status_code \
			+ '\tJSON: %s\n' %utils.getMsgOrFalse(r)
		return 'Unknown'

def setBindIp(port, ips):
	url = str(port) + '/binding-ips'
	data = {'ipset':ips}
	r = Put(url, data)
	if(r.status_code == 201):
		if(getProxyStatus(port) == 'Running'):
			return restartProxy(port)
		else:
			return True
	elif(r.status_code == 800):
		print '[FAILED]Backend.setBindIp(): RequestsError\n'
		return False
	else:
		print '[FAILED]Backend.setBindIp():\n'  \
			+ '\tUrl: %s\n'  %url \
			+ '\tIPs: %s\n'  %ips \
			+ '\tStatus Code: %s\n' %r.status_code \
			+ '\tJSON: %s\n' %utils.getMsgOrFalse(r)
		return False

def setProxyAuth(port, authpair):
	url = str(port) + '/user-passwd'
	data = {'userpasswd':authpair}
	r = Put(url, data)
	if(r.status_code == 201):
		if(getProxyStatus(port) == 'Running'):
			return restartProxy(port)
		else:
			return True
	elif(r.status_code == 800):
		print '[FAILED]Backend.setProxyAuth(): RequestsError\n'
		return False
	else:
		print '[FAILED]Backend.setProxyAuth():\n'  \
			+ '\tUrl: %s\n'  %url \
			+ '\tIPs: %s\n'  %ips \
			+ '\tStatus Code: %s\n' %r.status_code \
			+ '\tJSON: %s\n' %utils.getMsgOrFalse(r)
		return False

def getDataUsage(port):
	url = str(port) + '/data-usage'
	r = Get(url)
	if(r.status_code == 201):
		return r.json()['data-usage']
	elif(r.status_code == 800):
		print '[FAILED]Backend.getDataUsage(): RequestsError\n'
		return False
	else:
		print '[FAILED]Backend.getDataUsage():\n'  \
			+ '\tUrl: %s\n' %url \
			+ '\tStatus Code: %s\n' %r.status_code \
			+ '\tJSON: %s\n' %utils.getMsgOrFalse(r)
		return False

def updateData(user):
	deltaData = getDataUsage(user.port)
	print deltaData
	if(deltaData is False):
		return False
	user.data = user.data - deltaData
	user.save()
	if(user.data <= 0):
		stopProxy(user.port)
	return user.data

def updateAllData():
	allUser = models.CrossLanUser.objects.all()
	for u in allUser:
		print u.user.username
		updateData(user=u)



# Cron Classes

class UpdateDataCronJob(CronJobBase):
	RUN_EVERY_MINS = 30

	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'crosslan.UpdateDataCronJob'

	def do(self):
		msg = ''
		try:
			allUser = models.CrossLanUser.objects.all()
			for u in allUser:
				dataDelta = getDataUsage(u.port)
				if(dataDelta is not False):
					u.data = u.data - dataDelta
					u.save()
					if(u.data <= 0):
						stopProxy(u.port)
					dataDelta = utils.getHuman(dataDelta)
				else:
					dataDelta = 'Update Failed.'
				msg = msg + u.user.username + ': ' + dataDelta + '\n'
			return msg
		except Exception, e:
			return traceback.format_exc()
