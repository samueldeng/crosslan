from crosslan import models, conf
from django.db.models import Max
# Generates a "SELECT MAX..." statement

from ipware.ip import get_ip

import hashlib
import datetime
import re

SIGNAL_SIGNOUT = False

def getNextPort():
	pMax = models.CrossLanUser.objects.all().aggregate(Max('port'))['port__max']
	if(pMax >= conf.PORT_MAX):
		return -1
	else:
		return pMax+1

def unique(l):
	tmpList = list(set(l))
	tmpList.sort(key=l.index)
	return tmpList

def getHuman(balance):
	step = 0
	while(balance > 1000):
		balance = balance / 1000.0
		step = step + 1
	balance = str(balance)[:3]
	unit = ''
	if (step==0):
		unit = 'B'
	elif (step==1):
		unit = 'KB'
	elif (step==2):
		unit = 'MB'
	elif (step==3):
		unit = 'GB'
	elif (step==4):
		unit = 'TB'
	else:
		return 'Infinite'
	return balance + unit

def getClientIp(request):
	return get_ip(request)

def genRedeem():
	chars = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
	'0','1','2','3','4','5','6','7','8','9',
	'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
	amount = 100
	for i in range(25):
		md5 = hashlib.md5()
		md5.update(str(datetime.datetime.now()))
		mdStr = md5.hexdigest()
		results = []
		for i in range(4):
			subStr = mdStr[i*8:(i+1)*8]
			subDig = long(subStr, 16)
			subDig = subDig & 0x3FFFFFFF
			myUrl = ''
			for j in range(6):
				mask = 0x3D
				char = chars[subDig & mask]
				myUrl = myUrl + char
				subDig = subDig >> 5
			results = results + [myUrl]
		for i in results:
			try:
				models.RedeemCode.objects.new_code(i, models.RedeemCode.ACTIVE)
			except:
				amount = amount - 1
	return amount
