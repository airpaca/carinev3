import os
import config
import json
from django.contrib.gis.db import models
import datetime

# Create your models here.
class Expertise(models.Model):

    #id_expertise=models.AutoField(primary_key=True)
    id_source=models.ForeignKey('TypeSourceRaster',verbose_name="id de la source",default=None)
    #daterun = models.DateField()
    #pol = models.CharField(max_length=10)
    #ech = models.IntegerField()
    date_valid=models.DateField(default=None)
    delta = models.IntegerField()
    mn = models.IntegerField(default=None, null=True)  # limit min
    mx = models.IntegerField(default=None, null=True)  # limit max
    geom = models.GeometryField(srid=4326)

    def getSource(self):
        return TypeSourceRaster.objects.filter(id=self.id_source)
    
    def __str__(self):
        return (f"Expertise({self.id}, source {self.id_source}")

    @property
    def json(self):
        
        """Object as JSON data."""
        return dict(delta=self.delta, mn=self.mn, mx=self.mx,
                    geom=json.loads(self.geom.json))

class TypeSourceRaster(models.Model):
    #value pour intrun à check dans getdate
    #0,1,2 = j0, j-1, j-2
    
    intrun = models.IntegerField(default=999)
    pol = models.CharField(max_length=10)
    ech = models.IntegerField()
    type = models.CharField(max_length=10)
    is_default_source=models.BooleanField(default=False)
    statut=models.BooleanField(default=False)
    def getDate(self):
        if self.intrun in [0,1,2]:
            daterun=datetime.datetime.today() - datetime.timedelta(days=self.intrun)
            return daterun
        else :
            return "intrun " + str(self.intrun) + "invalide (doit etre 0, 1, ou 2)"
    
    def url(self):
        """Get path of a specific raster."""
        daterun = self.getDate()
        prefx = 'm' if self.ech < 0 else 'p'
        absech = abs(self.ech)
        path = os.path.join(
            config.DIR_RASTERS,
            f'raster_AURA_{self.pol}_{daterun:%d_%m_%Y}_j{prefx}{absech}_{self.type}.tif')
        return path
    
    def checkStatut(self):
        if os.path.exists(self.url()):
            return True
        else :
            return False
            
    def __str__(self):
        return self.url()
        
    @property
    def json(self):
        daterun = self.getDate()
        """Object as JSON data."""
        return dict(url=self.url(), daterun=f'{daterun:%d_%m_%Y}', pol=self.pol, ech=self.ech, type=self.type,is_default_source=self.is_default_source, statut=self.statut, intrun=self.intrun)
        
# class Source(models.Model):
    # #id_source=models.AutoField(primary_key=True)
    # type_source_raster=models.ForeignKey(TypeSourceRaster,default=None)
    # url=models.CharField(max_length=200,default="")
    # date_create=models.DateField(default=datetime.datetime.today())
    # is_source=models.BooleanField(default=False)
    # statut=models.BooleanField(default=False)

        
    # def checkStatut(self):
        # if os.path.exists(self.url):
            # return True
        # else :
            # return False
    # def getExpertises(self):
        # return Expertise.objects.Filter(id=self.id)
    
    # def get_is_source(self):
        # return self.type_source_raster.is_default_source 

    
    # def __str__(self):
        # return self.url
        
    # def json(self):
        # d=dict([('url',self.url),('is_source',self.is_source),('statut',self.statut)])
        # return d
    
 # class Previ(models.Model):
 
	# date_previ=models.DateField(default=None)	
	# pm10_0=models.ForeignKey('TypeSourceRaster',default=None)
	# pm10_1=models.ForeignKey('TypeSourceRaster',default=None)
	# pm10_2=models.ForeignKey('TypeSourceRaster',default=None)
	# o3_0=models.ForeignKey('TypeSourceRaster',default=None)
	# o3_1=models.ForeignKey('TypeSourceRaster',default=None)
	# o3_2=models.ForeignKey('TypeSourceRaster',default=None)
	# no2_0=models.ForeignKey('TypeSourceRaster',default=None)
	# no2_1=models.ForeignKey('TypeSourceRaster',default=None)
	# no2_2=models.ForeignKey('TypeSourceRaster',default=None)	
	# validee=False
	
	
	