import os
import config
import json
from django.contrib.gis.db import models
import datetime
import django.utils.timezone
import libcarine3.timestamp
from django.contrib.auth.models import User

class TypeSourceRaster(models.Model):
    #value pour intrun à check dans getdate
    #0,1,2 = j0, j-1, j-2
    
    intrun = models.IntegerField(default=999)
    pol = models.CharField(max_length=10)
    ech = models.IntegerField()
    type = models.CharField(max_length=10)
    is_default_source=models.BooleanField(default=False)

        
    @property
    def json(self):

        """Object as JSON data."""
        return dict(pol=self.pol, ech=self.ech, type=self.type,is_default_source=self.is_default_source, intrun=self.intrun)

class Source(models.Model):
    tsr=models.ForeignKey(TypeSourceRaster,default=None)
    daterun=models.IntegerField(default=0)
    commentaire=models.CharField(max_length=10000,default="")
    statut=models.BooleanField(default=False) 
    def checkStatut(self):
        if os.path.exists(self.url()):
            self.statut=True
            return True
        else :
            self.statut=False
            return False

    def url(self):
        """Get path of a specific raster."""
        prefx = 'm' if self.tsr.ech < 0 else 'p'
        absech = abs(self.tsr.ech)
        path = os.path.join(
            config.DIR_RASTERS,
            # f'raster_AURA_{self.pol}_{daterun:%d_%m_%Y}_j{prefx}{absech}_{self.type}.tif')
            f'{config.raster_prefix}_{self.tsr.pol}_{self.daterun}_j{prefx}{absech}_{self.tsr.type}.tif')
        return path
    
    def __str__(self):
        return self.url()
        
    def json(self):
        self.statut=self.checkStatut()
        url=self.url()
        """Object as JSON data."""
        return dict(url=url, daterun=self.daterun, pol=self.tsr.pol, ech=self.tsr.ech, type=self.tsr.type, intrun=self.tsr.intrun,statut=self.statut)
class Prev(models.Model):
    date_prev=models.IntegerField(default=libcarine3.timestamp.getTimestamp(0))
    pol=models.CharField(max_length=10,null=True)
    ech=models.IntegerField(null=True)
    src=models.ForeignKey(Source,on_delete=models.SET_NULL,null=True)

    def json(self):
        return dict(date_prev=self.date_prev,pol=self.pol,ech=self.ech,src=self.src.url())
class Expertise(models.Model):

    target=models.ForeignKey(Source,null=True)

    delta = models.IntegerField()
    mn = models.IntegerField(default=None, null=True)  # limit min
    mx = models.IntegerField(default=None, null=True)  # limit max des concentrations à modifier
    geom = models.GeometryField(srid=3857)
    ssup = models.IntegerField(default=None, null=True)  # sueil sup a pas dépasser
    smin = models.IntegerField(default=None, null=True)
    user = models.ForeignKey(User,default=None, null=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return ("Expertise="+str(self.id)+", source = " + str(self.target.id))

    @property
    def json(self):
        
        """Object as JSON data."""
        return dict(delta=self.delta, mn=self.mn, mx=self.mx,
                    geom=json.loads(self.geom.json))        


        
class IndiceCom(models.Model):
    indice=models.FloatField()
    prev=models.ForeignKey(Prev,null=True)
    code_insee=models.CharField(max_length=20,default="00000")
    def json_less(self):
        return(dict(code_commune=str(self.code_insee),indice=str(self.indice)))    
    def __str__(self):
        return self.json_less()

class DepassementReg(models.Model):
    source=models.ForeignKey(Source)
    id_zone=models.IntegerField(default=999)
    resultat=models.BooleanField()
    def __str__(self):
        return self.str(id_zone)
        
class DatePrev(models.Model):
    date_prev=models.IntegerField(default=libcarine3.timestamp.getTimestamp(0))
    commentaire=models.CharField(max_length=10000,null=True,default=None)
    previsionniste=models.CharField(max_length=100,null=True,default=None)
class Polluant(models.Model):
    nom=models.CharField(max_length=10,null=True,default=None)
    lib=models.CharField(max_length=100,null=True,default=None)
    val=models.IntegerField(default=None,null=True)
    vls=models.FloatField(default=None,null=True)
    ale=models.FloatField(default=None,null=True)
    colormap= models.CharField(max_length=1000,null=True,default=None)