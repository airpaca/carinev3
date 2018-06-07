import os
import config
import json
from django.contrib.gis.db import models
import datetime
import django.utils.timezone
import libcarine3.timestamp
from django.contrib.auth.models import User
import os
class TodayState(models.Model):
	date=models.DateField(auto_now_add=True)
	file_ok=models.BooleanField(default=False)
	valid_en_cours = models.BooleanField(default=False)
class DicoPath(models.Model):
	nom=models.CharField(max_length=20,default='')
	desc=models.CharField(max_length=200,default='')
	sep=models.CharField(max_length=1,default='')
	ext=models.CharField(max_length=10,default='')
	suffixe=models.CharField(max_length=10,default='')
	def __str__(self):
		return self.nom
	def get_file_url(self,pref,poll,tsp,ech):
		last_sep=self.sep
		if self.suffixe == "''":
			last_sep = ''
			self.suffixe = ''
		elif self.suffixe == "":
			last_sep = ''
			self.suffixe = ''
		print (self.suffixe)
		print(last_sep)
		return pref + self.sep + poll + self.sep + str(tsp) + self.sep + str(ech) + last_sep + self.suffixe+ '.' + self.ext
class RemoteMachine(models.Model):
	nom=models.CharField(max_length=20,default='')
	domaine=models.CharField(max_length=20,default='')
	user = models.CharField(max_length=20,default='')
	dir=models.CharField(max_length=200,default='')
	type=models.ForeignKey(DicoPath,default=None)
	active=models.BooleanField(default=True)
	def get_list(self):
		return [self.domaine,self.user,self.dir]
	def get_scp_string(self):
		s=self.user+"@"+self.domaine+":"+self.dir
		return s
	def __str__(self):
		return self.nom

class OutputData(models.Model):
	desc=models.CharField(max_length=200,default='')
	type=models.ForeignKey(DicoPath,default=None)
	dir=models.CharField(max_length=200,default='')
	def __str__(self):
		return self.type.nom
	def get_local_dir(self,outdir):
		dir=os.path.join(outdir,self.dir)
		return dir
	
	
class Previ_mod(models.Model):
	nom=models.CharField(max_length=200,default='')
	output_dir=models.CharField(max_length=200,default='/var/www/html/')
	DIR_RASTERS = models.CharField(max_length=200,default='/home/previ/raster_source')
	DIR_RASTERS_GLOB = models.CharField(max_length=200,default='/home/previ/raster_source')
	raster_prefix = models.CharField(max_length=200,default='AURA')
	profile={'count':1,'height':300,'width':400,'driver':'GTiff','transform':[1425, 0.0, 229638.54496787317, 0.0, -1425, 5910187.041501439]}
	geom_field = "the_geom"
	polls=['NO2','PM10','O3','MULTI']
	hd_dest=models.CharField(max_length=200,default='')
	hd_path=models.CharField(max_length=200,default='/var/www/html/hd/') 
	hd_val_path=models.CharField(max_length=200,default='/var/www/html/hd/val')
	basse_def_path=models.CharField(max_length=200,default='/var/www/html/basse_def/')
	basse_def_val_path=models.CharField(max_length=200,default="/var/www/html/basse_def/val/") 
	basse_def_url=models.CharField(max_length=200,default='')
	basse_def_url_val_path=models.CharField(max_length=200,default='')
	public_adresse=models.CharField(max_length=200,default='')
	echs_diff=[-1,0,1,2]    
	launch_smile_prod=models.CharField(max_length=200,default="")
	launch_smile_preprod=models.CharField(max_length=200,default="")
	mylogs=models.CharField(max_length=200,default="/var/www/html/mylogs.txt")
	fpop=r'/home/previ/raster_source/pop/pop100m_2154.tif' #views.py l-553 716
	disp=r'/home/previ/vector_source/disp_reg_aura.shp' # pareil
	fpop_com=r'/home/previ/raster_source/pop/pop_com_lyonok.tif' # views.py 717
	disp=r'/home/previ/vector_source/communes_geofla_light.shp' # 729
	lyon_arr = r'/home/previ/vector_source/lyon_geofla_arr.shp' # 730
	machines = models.ManyToManyField(RemoteMachine)
	###### preprocessing.py
	src_2154='/home/previ/raster_source/ada/2154/' 
	f_3857 = '/home/previ/raster_source/'
	f_temp = '/home/previ/raster_source/ada/3857/'
	bbox_aura ='/home/previ/vector_source/bbox_aura_3857.shp'
	aura_cutline='/home/previ/vector_source/aura_reg_3857.shp'
	##### subprocess_wrapper
	colormap_file='/var/www/html/carinev3/libcarine3/colormaps/normalize_colors.txt'
	def __str__(self):
		return self.nom
class Fine_echelle_mod(models.Model):
	nom=models.CharField(max_length=200,default='')
	dirFine = models.CharField(max_length=200,default='/home/previ/raster_source/domaines_fine/3857',null=True)
	dirFineCustom=models.CharField(max_length=200,default='/home/previ/raster_source/domaines_fine/3857/custom',null=True)
	raster_prefix = models.CharField(max_length=200,default='AURA',null=True)
	hd_dest=models.CharField(max_length=200,default='',null=True)
	hd_path=models.CharField(max_length=200,default='/var/www/html/hd/',null=True) 
	hd_val_path=models.CharField(max_length=200,default='/var/www/html/hd/val',null=True) 
class BassinGrenoblois(models.Model):
	host=models.CharField(max_length=200,default='')
	user=models.CharField(max_length=200,default='')
	db=models.CharField(max_length=200,default='')
	password=models.CharField(max_length=200,default='')
	table=models.CharField(max_length=200,default='')
class Context(models.Model):
	nom=models.CharField(max_length=200,default='') 
	previ_mod=models.ForeignKey(Previ_mod,default=None)   
	fine_mod=models.ForeignKey(Fine_echelle_mod,null=True,blank=True)
	api_active=models.BooleanField(default=False)
	previ_active=models.BooleanField(default=False)
	bassin_grenoblois = models.ForeignKey(BassinGrenoblois,null=True,blank=True)
	active=models.BooleanField(default=False)
	def __str__(self):
		return self.nom
  
class DomaineFine(models.Model):
	nom=models.CharField(max_length=100,default="")
	libCourt=models.CharField(max_length=100,default="")
	libLong=models.CharField(max_length=100,default="")
	def __str__(self):
		return self.nom
class Echeance(models.Model):
	delta=models.IntegerField(null=True)
	libChar=models.CharField(max_length=10,default="")
	libInt=models.CharField(max_length=10,default="")
	
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
	note=models.CharField(max_length=10000,null=True)
	def get_urls(self):
		outD = OutputData.objects.all()
		for i in outD:
			#prev poll tsp ech
			ctx = Context.objects.filter(active = True)
			
			pref = ctx[0].previ_mod.raster_prefix
			bname = i.type.get_file_url(pref,self.pol.lower(),self.date_prev,self.ech+1)
		return dict(nom = i.type.nom, url = os.path.join(ctx[0].previ_mod.output_dir,os.path.join(i.dir,bname)))
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
	

class DalleFine(models.Model):
	poll=models.ForeignKey(Polluant,null=True)
	nom=models.ForeignKey(DomaineFine,null=True)
	ech = models.ForeignKey(Echeance,null=True)
	date_prev = models.ForeignKey(DatePrev,null=True)
	is_valid=models.BooleanField(default=True)
	def get_url_fine(self):
		dname = config.dirFine
		bname = config.raster_prefix + '_'+ self.poll.nom + '_'  + self.nom.libLong + '_'+ str(self.date_prev.date_prev) + '_' +self.ech.libChar + '_3857.tif'
		url = os.path.join(dname,bname)
		return url
	def get_url_mi_fine(self):
		dname = config.raster_dirFineCustom       
		bname = config.raster_prefix + '_' + self.poll.nom +  '_'  + self.nom.libLong + '_'+ str(self.date_prev.date_prev) + '_' +self.ech.libChar + '_3857_custom.tif'
		url = os.path.join(dname,bname)
		return url
	def get_status(self):
		status=False
		url = self.get_url_fine()
		if (os.path.exists(url)):
			status = True
		return status
	def __str__(self):
		return self.get_url_fine()