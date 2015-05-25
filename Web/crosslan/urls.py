from django.conf.urls import patterns,  url

from crosslan import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^signup/$', views.signup, name='signup'),
	url(r'^signin/$', views.signin, name='signin'),
	url(r'^signout/$', views.signout, name='signout'),
	url(r'^info/$', views.info, name='info'),
	url(r'^info/refresh/$',views.refreshInfo, name='refresh'),
	url(r'^info/rebind/$',views.rebindIp, name='rebind'),
)
