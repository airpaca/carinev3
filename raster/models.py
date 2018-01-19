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
    def url_source(self):
        t=self.tsr.type
        p=self.tsr.pol
        ech=self.tsr.ech
        ech_lib=config.libs_ech[ech+1]
        f_name=''
        if (self.tsr.type == 'prev'):
            f_name='prev/' +config.raster_prefix +'_prevair_4km_' + p.upper() + '_' + str(self.daterun) + '_' + ech_lib + '.tif'
        elif ( self.tsr.type == 'ada' ): 
            f_name='ada/' + config.raster_prefix +'_adapstat_' + p.upper() + '_' + str(self.daterun) + '_' + ech_lib + '.tif'
        elif ( self.tsr.type == 'chim' ): 
            f_name='chimere/' + config.raster_prefix +'_chimere_' + p.upper() + '_' + str(self.daterun) + '_' + ech_lib + '.tif' 
            
        else :
            pass
        url=os.path.join(config.DIR_RASTERS_GLOB,f_name)
        return url
    def url_2154(self):
        t=self.tsr.type
        p=self.tsr.pol
        ech=self.tsr.ech
        ech_lib=config.libs_ech[ech+1]
        f_name=''
        if (self.tsr.type == 'prev'):
            f_name='prev/2154/' +config.raster_prefix+'_prevair_4km_' + p.upper() + '_' + str(self.daterun) + '_' + ech_lib + '_2154.tif'
        elif ( self.tsr.type == 'ada' ): 
            f_name='ada/2154/' + config.raster_prefix +'_adapstat_' + p.upper() + '_' + str(self.daterun) + '_' + ech_lib + '_2154.tif'
        elif ( self.tsr.type == 'chim' ): 
            f_name='chimere/2154/' + config.raster_prefix +'_chimere_' + p.upper() + '_' + str(self.daterun) + '_' + ech_lib + '_2154.tif' 
        elif ( self.tsr.type == '' ): 
            f_name='multi/' + config.raster_prefix +'_multi_' + p.upper() + '_' + str(self.daterun) + '_' + ech_lib + '.tif'            
            
        else :
            pass
        url_2154=os.path.join(config.DIR_RASTERS,f_name)
        return url_2154
        
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
    lib=models.CharField(max_length=200,default="00000")
    def json_less(self):
        return(dict(code_commune=str(self.code_insee),indice=str(self.indice)))    


class Zone(models.Model):
    id_zone=models.IntegerField(default=0)
    pop=models.FloatField(default=0)
    surf=models.FloatField(default=0)
    lib=models.CharField(max_length=50,default="")
    
class DepassementReg(models.Model):
    prev=models.ForeignKey(Prev,default=None)
    zone=models.IntegerField(default=None, null=True)
    lib=models.CharField(max_length=200,default="00000")    
    pop_exp_info=models.FloatField(default=0)
    surf_exp_info=models.FloatField(default=0)
    pop_exp_perc_info=models.FloatField(default=0)
    surf_exp_perc_info=models.FloatField(default=0)
    pop_exp_alerte=models.FloatField(default=0)
    surf_exp_alerte=models.FloatField(default=0)
    pop_exp_perc_alerte=models.FloatField(default=0)
    surf_exp_perc_alerte=models.FloatField(default=0)
    depassement_pop_info=models.BooleanField(default=False)
    depassement_surf_info=models.BooleanField(default=False)
    depassement_pop_alerte=models.BooleanField(default=False)
    depassement_surf_alerte=models.BooleanField(default=False)
    def json(self):
        dct= dict(
            date=self.prev.date_prev,
            zone=self.zone,
            pop_exp_info=self.pop_exp_info,
            pop_exp_perc_info=self.pop_exp_perc_info,
            surf_exp_info=self.surf_exp_info,
            surf_exp_perc_info=self.surf_exp_perc_info,
            pop_exp_alerte=self.pop_exp_alerte,
            pop_exp_perc_alerte=self.pop_exp_perc_alerte,
            surf_exp_alerte=self.surf_exp_alerte,
            surf_exp_perc_alerte=self.surf_exp_perc_alerte,
            depassement_pop_info=self.depassement_pop_info,
            depassement_surf_info=self.depassement_surf_info,
            depassement_pop_alerte=self.depassement_pop_alerte,
            depassement_surf_alerte=self.depassement_surf_alerte
            )
        return dct
    def __str__(self):
        return self.json()
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