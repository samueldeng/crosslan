from django.contrib import admin
from crosslan.models import CrossLanUser, BindingIP, RedeemCode

# Register your models here.
class BindingIPInline(admin.TabularInline):
	model = BindingIP
	extra = 1

class UserAdmin(admin.ModelAdmin):
	fieldsets = [
		('User', {'fields' : ['user']}),
		('Proxy', {'fields' : ['host', 'port']}),
		('Data left', {'fields':['data']}),
		('Bind or Not', {'fields' : ['bind']}),
	]
	inlines = [BindingIPInline]

class RedeemAdmin(admin.ModelAdmin):
	fieldsets = [
		('Code', {'fields' : ['code']}),
		('Status', {'fields' : ['status']}),
	]

admin.site.register(CrossLanUser, UserAdmin)
admin.site.register(RedeemCode, RedeemAdmin)
