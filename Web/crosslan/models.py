from django.db import models
from django.conf import settings

from crosslan import conf

class CrossLanUserManager(models.Manager):
    def create_user(self, user, host, port):
        user = self.create(user=user, host=host, port=port)
        return user

class CrossLanUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    host = models.CharField('Proxy Address', max_length=20, default=conf.PROXY_HOST)	# May not be necessary
    port = models.IntegerField('Proxy Port', unique=True)
    data = models.IntegerField('Data Balance', default=0)
    last_update = models.DateTimeField('Last Update Time', auto_now=True)
    bind = models.BooleanField('Bind or Not', default=False)

    objects = CrossLanUserManager()

    def __unicode__(self):
    	return self.user.__unicode__()

class BindingIPManager(models.Manager):
	def bind_ip(self, user, ip):
		bindIp = self.create(user=user, ip=ip)
		return bindIp

class BindingIP(models.Model):
	user = models.ForeignKey(CrossLanUser, verbose_name='The User binding to')
	ip = models.CharField('Client IP binding to User', max_length=20)

	objects = BindingIPManager()

	def __unicode__(self):
		return self.ip

class RedeemManager(models.Manager):
	def new_code(self, code, status="IN"):
		redeem = self.create(code=code, status=status)
		return redeem

class RedeemCode(models.Model):
	code = models.CharField('Redeem Code', max_length=6, unique=True);

	INACTIVE = 'IN'
	ACTIVE = 'AC'
	USED = 'US'
	STATUS_CHOICES = (
		(INACTIVE, 'Inactive'),
		(ACTIVE, 'Active'),
		(USED, 'Code Used'),
	)
	status = models.CharField(max_length=2,
		choices=STATUS_CHOICES,
		default=INACTIVE)

	objects = RedeemManager()

	def use(self):
		if(self.status==self.ACTIVE):
			self.status = self.USED
			return True

	def activate(self):
		if(self.status==self.INACTIVE):
			self.status = self.ACTIVE
			return True

	def recycle(self):
		if(self.status==self.USED):
			self.status = self.ACTIVE
			return True
