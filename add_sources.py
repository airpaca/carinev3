from raster.models import TypeSourceRaster  as tsr

intrun=[0,1,2]
ech=[-1,0,1,2]
type=['ada','fine','prev','chim']
polls=['NO2','O3','PM10']
default_source='ada'


for i in intrun:
    for j in ech:
        for p in polls:
            for t in type:
                ts=tsr(intrun=i,ech=j,pol=p,type=t)
                if (i==0):
                    if (j<2):
                        if (t==default_source):
                            ts.is_default_source=True;
                ts.save()