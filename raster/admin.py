from django.contrib import admin
from .models import Expertise,TypeSourceRaster,Source,IndiceComVersion,Prev

# Register your models here.
admin.site.register(Expertise)
admin.site.register(TypeSourceRaster)
admin.site.register(Source)
admin.site.register(Prev)
admin.site.register(IndiceComVersion)