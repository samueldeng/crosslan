from crosslan import conf
import requests, json, models

from django_cron import CronJobBase, Schedule

def Post(url, data):
	r = requests.post(conf.BACKEND_HOST + url, json.dumps(data))
	return r

def Put(url, data):
	r = requests.put(conf.BACKEND_HOST + url, json.dumps(data))
	return r

def Get(url):
	r = requests.get(conf.BACKEND_HOST + url)
	return r

def operateProxy(port, action):
	url = str(port) + '/running-status'
	data = {'action':action}
	r = Put(url, data)
	if(r.status_code == 201):
		return True
	else:
		return r.json()

# Here Begins Functions Communicate with Backend
def newUser(port):
	url = str(port)
	data = {}
	r = Post(url, data)
	if(r.status_code == 201):
		return True
	else:
		return False

def startProxy(port):
	return operateProxy(port, 'start')

def stopProxy(port):
	return operateProxy(port, 'stop')

def restartProxy(port):
	if(getProxyStatus(port) == 'Stopped'):
		return startProxy(port)
	return operateProxy(port, 'restart')

def setBindIp(port, ips):
	url = str(port) + '/binding-ips'
	data = {'ipset':ips}
	r = Put(url, data)
	restartProxy(port)
	if(r.status_code == 201):
		return True
	else:
		return False

def getProxyStatus(port):
	url = str(port) + '/running-status'
	r = Get(url)
	if(r.status_code == 201):
		if(r.json()['status'] == 'running'):
			return 'Running'
		else:
			return 'Stopped'
	else:
		return False

def getDataUsage(port):
	url = str(port) + '/data-usage'
	r = Get(url)
	if(r.status_code == 201):
		return r.json()['data-usage']
	else:
		return False

def updateData(user):
	try:
		deltaData = getDataUsage(user.port)
		if(deltaData is False):
			return False
		user.data = user.data - deltaData
		user.save()
		if(user.data <= 0):
			stopProxy(user.port)
		return user.data
	except Exception,e:
		return False

class CronTester(CronJobBase):
	RUN_EVERY_MINS = 1

	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'crosslan.CronTester'

	def do(self):
		print self.code


class UpdateDataCronJob(CronJobBase):
	RUN_EVERY_MINS = 30

	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'crosslan.UpdateDataCronJob'

	def do(self):
		allUser = models.CrossLanUser.objects.all()
		for u in allUser:
			updateData(user=u)
