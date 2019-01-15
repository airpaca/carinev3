from raster.models import DatePrev,Prev,Source,TypeSourceRaster 
from libcarine3 import timestamp
import libcarine3
import config
def add_tsr():
	intrun=[0,1,2]
	ech=[-1,0,1,2]
	type=['ada','fine','prev','chim']
	polls=['NO2','O3','PM10']
	default_source=['ada','']

	c=0
	for i in intrun:
		for j in ech:
			for p in polls:
				for t in type:
					ts=TypeSourceRaster(intrun=i,ech=j,pol=p,type=t)
					if (i==0):
						if (j<3):
							if (t in default_source):
								ts.is_default_source=True
								c+=1
					ts.save()
	for i in intrun:
		for j in ech:

			ts=TypeSourceRaster(intrun=i,ech=j,pol='MULTI',type='')
			if (i==0):
				if (j<3):
					ts.is_default_source=True
					c+=1
			ts.save()

	return c
	
# def init_today(run):
	# x=int(run)
	# d=libcarine3.timestamp.getTimestamp(x)
	# init l'object dateprev si y en a pas
	# if (len(DatePrev.objects.filter(date_prev=d))==0):
		# dp=DatePrev(date_prev=d)
		# dp.save()
		
	# p=Prev.objects.filter(date_prev=d)
	# if (len(p)==0):
		# for p in config.polls:
			# for e in config.echs_diff:
				# pr=Prev(date_prev=d,ech=e,pol=p)
				# pr.save()
		# ls={}
		# tsr=TypeSourceRaster.objects.all()
		# for i in tsr:
			# if (i.intrun==x):
				# s=Source(tsr=i,daterun=d)
				# s.statut=s.checkStatut()
				# s.save()
				# if (i.is_default_source):
					# p=i.pol
					# e=i.ech
					# prev=Prev.objects.get(date_prev=d,pol=p,ech=e)
					# prev.src=s
					# prev.save()
				# ls[s.id]=s.json()
	# return 'Nb dinstance de Prev : ' + str(len(p))
def init_from_to(min,max):
	c=0
	print(min)
	print(max)
	for i in range(max,min):
	
		init_today(i)
		c+=1
	return c
		
	
def init_today(run):
	x=int(run)
	print(x)
	d=libcarine3.timestamp.getTimestamp(x)
	print(d)
	if (len(DatePrev.objects.filter(date_prev=d))==0):
		dp=DatePrev(date_prev=d)
		print(dp)
		dp.save()
		for p in config.polls:
			for e in config.echs_diff:
				pr=Prev(date_prev=d,ech=e,pol=p)
				pr.save()
				print(pr)
	else :
		print(str(d) + " existe deja prev")
	ls={}
	tsr=TypeSourceRaster.objects.all()
	for i in tsr:
		
		s=Source(tsr=i,daterun=d)
		print(s)
		if (len(Source.objects.filter(daterun=d,tsr=i))==0):
			s.save()
			if (i.is_default_source):
				p=i.pol
				e=i.ech
				prev=Prev.objects.get(date_prev=d,pol=p,ech=e)
				prev.src=s
				prev.save()
			ls[s.id]=s.json()
		else :
			print(str(d) + " existe deja tsr")
	return ls

# def init_today(run):
	# x=int(run)
	# d=libcarine3.timestamp.getTimestamp(x)
	# if (len(DatePrev.objects.filter(date_prev=d))==0):
		# dp=DatePrev(date_prev=d)
		# dp.save()
		# for p in config.polls:
			# for e in config.echs_diff:
				# pr=Prev(date_prev=d,ech=e,pol=p)
				# pr.save()
	# else :
		# print(str(d) + " existe deja prev")
	# ls={}
	# tsr=TypeSourceRaster.objects.all()
	# for i in tsr:
		# s=Source(tsr=i,daterun=d)
		# if (len(TypeSourceRaster.objects.filter(daterun=d))==0):
			# s.save()
			# if (i.is_default_source):
				# p=i.pol
				# e=i.ech
				# prev=Prev.objects.get(date_prev=d,pol=p,ech=e)
				# prev.src=s
				# prev.save()
			# ls[s.id]=s.json()
	# else :
		# print(str(d) + " existe deja tsr")
	# return ls
