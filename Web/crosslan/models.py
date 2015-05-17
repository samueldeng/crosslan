from django.db import models
from django.conf import settings

class CrossLanUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    host = models.CharField('Proxy Address', max_length=20)	# May not be necessary
    port = models.IntegerField('Proxy Port', default=0)
    data = models.IntegerField('Data Balance', default=0)
    bind = models.BooleanField('Bind or Not', default=False)

class BindingIP(models.Model):
	user = models.ForeignKey(CrossLanUser, verbose_name='The User binding to')
	ip = models.CharField('Client IP binding to User', max_length=20)
