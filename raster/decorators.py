from .models import *
from .accueil_views import accueil
from datetime import date
def check_today_state(function):
	def wrap(request, *args, **kwargs):
		ts=TodayState.objects.filter(date=date.today())
		if (len(ts)>0):
			if ts[0].file_ok == True :
				return function(request, *args, **kwargs)
			else :
				return accueil(request)
		else :
			return accueil(request)
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap