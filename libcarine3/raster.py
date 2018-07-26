#!/usr/bin/env python3
# coding: utf-8

"""Carine v3 :: raster"""


import io
import logging
import rasterio as rio
from rasterio import features
import numpy as np
import matplotlib.pyplot as plt
import libcarine3
from libcarine3 import colors
import config
import os
from raster import models
import affine
from rasterio.io import MemoryFile
from datetime import date
log = logging.getLogger('libcarinev3.raster')


def rasterize_zt(poly, rstshape, rstaff):
	"""Création d'un raster d'une zone tampon autour d'un polygone.
	
	:param poly: Polygon.
	:param distance: distance.
	:param rstshape: shape of output.
	:param rstaff: transformation of raster.
	:return: np.array.
	"""
	pbuf = poly
	log.debug(poly)
   
	shapes = ((g, 255) for g in [pbuf])
	# log.debug("------------------------------------------------------------------")
	# log.debug(next(shapes))
	rbuf = features.rasterize(shapes=shapes,
							  out_shape=rstshape,
							  transform=rstaff,default_value=1,
							  all_touched=False)

	return rbuf
# def rasterize(poly, rstshape, rstaff):

	# shapes = ((g, 1) for g in [poly])
	# rbuf = features.rasterize(shapes=shapes,
							  # out_shape=rstshape,
							  # transform=rstaff,
							  # all_touched=True)
	# return rbuf
def to_png(data, fn=None, dpi=10):
	"""Convert raster into png format.
	
	:param fn: path and filename of output png file or None
	:param dpi:
	:return: None or Pillow.Image if fn is None.
	"""

	# Create figure
	log.debug("ljhf")
	figsize = (data.shape[1] /dpi, data.shape[0]/dpi)
	log.debug(figsize)
	fig = plt.figure(frameon=False, figsize=figsize,dpi=dpi)
	ax = fig.add_axes([0, 0, 1, 1])
	ax.axis('off')

	# Echelle de couleurs
	cmap = libcarine3.colors.discrete_cmap(libcarine3.colors.colors)
	vmin = 0
	vmax = np.max(data)


	plt.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
	log.debug("creating plot done!")

	# Export sous forme d'image
	f = open(fn, 'wb') if fn else io.BytesIO()

	fig.canvas.print_png(f)

	fig.clf()

	plt.close()
	if fn:
		f.close()
		log.debug(f"save image to {fn}")
	else:
		log.debug("return image data...")
		return f.getvalue()

class Raster:
	"""Raster."""

	def __init__(self, fn, pol,source=None,epsg=None):
		"""Raster.
		
		:param fn: path and filename of a raster.
		:param pol: pollutant id.
		"""
		
		self.fn = fn

		self.r = rio.open(self.fn, 'r')
		
		if pol not in config.POLLUTANTS:
			log.error("cannot reconize pollutant! " + pol)
			raise libcarine3.Carinev3Error("cannot reconize pollutant! " + pol)
		self.pol = pol
		self.expertises = list()
		self.source=source
		self.epsg=epsg

	def __del__(self):
		"""Close raster."""
		self.r.close()


	@property
	def x(self):
		x, _ = np.meshgrid(self.xs, self.ys)
		return x

	@property
	def y(self):
		_, y = np.meshgrid(self.xs, self.ys)
		return y
		
	def get_array(self):
		data = self.r.read(1)

		mask = (data == self.r.nodata)
		shape=self.r.shape
		aff=self.r.transform
		# self.r.close()
		#data = np.ma.array(data, mask=mask)
		del mask
		bascule_exp_order = date(2018,7,26)
		if (self.source != None):
			if (date.fromtimestamp(self.source.daterun) < bascule_exp_order):
				self.expertises = self.expertises[::-1]
		# Apply modifications
		for expertise in self.expertises:
			if (expertise.active==True):
				log.debug("**************** EXPERTISE *********************")
				log.debug(expertise)
				print(expertise)
				modif = np.zeros(data.shape)

				# if expertise.ssup:
					# mk_ssup = (modif+expertise.delta) <= expertise.ssup
				# else:
					# mk_ssup = (data > 0)
				# Use mask if mn or mx
				# FIXME: comment faire le traitement avec les bornes min et max
				# if expertise.smin:
					# mk_smin = (data + expertise.delta > expertise.mn)
				# else : 
					# mk_smin = (data > 0)
					
				if expertise.mn > 0:
					mk_mn = (data >= expertise.mn)
					
				else:
					mk_mn = (data > 0)
				   
				if expertise.mx < 9999:
					mk_mx = (data <= expertise.mx)

				else:
					mk_mx = (data > 0)
					
				if expertise.geom.geom_type == 'Point':
					g = libcarine3.Point(*expertise.geom.coords, epsg=4326)
			
				elif expertise.geom.geom_type == 'Polygon':
					if (self.epsg==None):
						g = libcarine3.Polygon(expertise.geom.coords[0], epsg=3857)
					else :
						g1 = libcarine3.Polygon(expertise.geom.coords[0], epsg=3857)
						g=g1.reproject(epsg=2154)

				else:
					raise NotImplementedError()
				rbuf = rasterize_zt(g,  shape, aff)			

				modif[(rbuf == 255) & mk_mn & mk_mx] = expertise.delta
				data += modif
				# print(np.max(data))
				# mk1=(data * (modif ==expertise.delta))
				#modif[mk_mx_ecret] = 100
				# if (expertise.mx < 9999):

					# print(np.max(mk1))
					# d2= (mk1 < expertise.mx) & (mk1 > 0)
					# print(' d2: ' + str(d2.shape))
					# print('mx : ' + str(expertise.mx)) 
					# data[d2] = expertise.mx
				
				# if (expertise.mn > 0):
					# d3= (mk1 > expertise.mn) 
					# print(' d3: ' + str(d3.shape))
					# print('mn : ' + str(expertise.mn)) 
					# data[d3] = expertise.mn
				
				# d3=mk1 < expertise.mn
				# print('mn : ' + str(expertise.mn)) 
				# print(' d3: ' + str(d3.shape))
				# data[d3] = expertise.mn
			
				
		print("get_array() end : " +str(np.min(data)))
		return data
	def sample_gen(self, x,y, indexes=None):
		#rewrite de la source du meme nom de rio (rio.sample.sample_gen) 
		index = self.r.index
		d = self.get_array()
		
		if isinstance(indexes, int):
			indexes = [indexes]
		r, c = index(x, y)
		window = ((r, r+1), (c, c+1))
		data = d[r][c]

		if (self.pol!=10):
			d=libcarine3.merge_tools.sous_indice(d,self.pol)
		
		data2=d[r][c]
		log.debug([data,data2])
		return([data,data2])
	def to_png(self,data, fn=None, dpi=10):
		"""Convert raster into png format.
		
		:param fn: path and filename of output png file or None
		:param dpi:
		:return: None or Pillow.Image if fn is None.
		"""
		mk=(data==255)
		data=np.ma.array(data,mask=mk)
		# Limits
		#data[(data > -999) & (data < 0)] = 0

		# Create figure
		log.debug("oiyouyiuy")
		#size en pouces
		figsize = (data.shape[1]/dpi, data.shape[0]/dpi)
		log.debug(figsize)
		fig = plt.figure(frameon=False, figsize=figsize)
		ax = fig.add_axes([0, 0, 1,1])
		ax.axis('off')
		# Echelle de couleurs
		cmap = libcarine3.colors.discrete_cmap(libcarine3.colors.colors)
		vmin = 0
		vmax = 100
		log.debug(vmax)
		print(data)
		print(libcarine3.colors.cmap)
		print(libcarine3.colors.norm)
		plt.imshow(data, cmap=libcarine3.colors.cmap, norm=libcarine3.colors.norm)
		log.debug("creating plot done cool !")

		# Export sous forme d'image
		f = open(fn, 'wb') if fn else io.BytesIO()

		fig.canvas.print_png(f)
		log.debug("print ok")
		fig.clf()
	
		plt.close()
		if fn:
			f.close()
			log.debug(f"save image to {fn}")
		else:
			log.debug("return image data...")
			return f.getvalue()

	def to_tif(self,data, fn=None, dpi=10):
		"""Convert raster into png format.
		
		:param fn: path and filename of output png file or None
		:param dpi:
		:return: None or Pillow.Image if fn is None.
		"""
	

		# Limits
		#data[(data > -999) & (data < 0)] = 0

		# Create figure
		log.debug("oiyouyiuy")
		#size en pouces
		log.debug(data.shape)
		data=data.reshape(data.shape[2],data.shape[1])
		figsize = (data.shape[1]/dpi, data.shape[0]/dpi)
		log.debug(figsize)
		fig = plt.figure(frameon=False, figsize=figsize)
		ax = fig.add_axes([0, 0, 1,1])
		ax.axis('off')

		# Echelle de couleurs
		cmap = libcarine3.colors.discrete_cmap(libcarine3.colors.colors)
		vmin = 0
		vmax = 100
		log.debug(vmax)
		# if (self.pol!=10):
			# data=libcarine3.merge_tools.sous_indice(data,self.pol)
		plt.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
		log.debug("creating plot done cool !")

		# Export sous forme d'image
		a=fig.savefig(fn)
		log.debug("print ok")
		
	
		plt.close()
		return a
	@property
	def bbox(self):
		"""Bounding box of raster.
		
		:return: (xmin, ymin, xmax, ymax).
		"""
		return list(self.r.bounds)

	def add_expertises(self, expertises):
		"""Add expertises.
		
		:param expertises: list of Expertises object.
		"""
		self.expertises += expertises
		
	def export_low_val(self,new_file):
		with rio.Env(GDAL_CACHEMAX=512,NUM_THREADS='ALL_CPUS') as env:

			pr = self.r.profile
			# pol=self.source.tsr.pol
			# ech=self.source.tsr.ech
			# tsp=self.source.daterun
			
			# new_file = config.basse_def_val_path + config.aasqa +'-'+ pol.lower() + '-' + str(tsp) + '-' + str(ech+1) + '.tiff' 
			log.debug(" --- new file --- ")
			log.debug(new_file)
			ar=self.r.read(1)
			new_ar = self.get_array()
			shp=new_ar.shape

			shp2=new_ar.shape
			aff=self.r.transform
			log.debug(pr)
			with rio.open(new_file,'w',**pr) as dst:
				dst.write(new_ar,1)
				dst.close()
			return 'toto'
			

	