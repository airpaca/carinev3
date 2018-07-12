from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Expertise)
admin.site.register(TypeSourceRaster)
admin.site.register(Source)
admin.site.register(Prev)

admin.site.register(DatePrev)
admin.site.register(Polluant)
admin.site.register(Zone)

admin.site.register(DomaineFine)
admin.site.register(Echeance)

admin.site.register(RemoteMachine)
admin.site.register(Previ_mod)
admin.site.register(Context)
admin.site.register(Fine_echelle_mod)
admin.site.register(BassinGrenoblois)
admin.site.register(DicoPath)
admin.site.register(OutputData)
admin.site.register(TodayState)