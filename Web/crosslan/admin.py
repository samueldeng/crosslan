from django.contrib import admin
from crosslan.models import CrossLanUser, BindingIP

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

admin.site.register(CrossLanUser, UserAdmin)
