from django.contrib import admin
from .models import Expertise,TypeSourceRaster,Source,Prev,DatePrev,Polluant,Zone

# Register your models here.
admin.site.register(Expertise)
admin.site.register(TypeSourceRaster)
admin.site.register(Source)
admin.site.register(Prev)

admin.site.register(DatePrev)
admin.site.register(Polluant)
admin.site.register(Zone)