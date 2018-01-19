from libcarine3 import subprocess_wrapper
import os
import subprocess
import rasterio as rio
def projcrop_ada(f):
    with rio.Env(GDAL_CACHEMAX=512,NUM_THREADS='ALL_CPUS') as env:
        bname=os.path.basename(f)
        dname=os.path.dirname(f)
        f_2154= '/home/previ/raster_source/ada/2154/'+bname[0:-4]+"_2154.tif"
        ls=bname[0:-4].split('_')               
        f_3857 = '/home/previ/raster_source/'+ls[0] + '_' + ls[2] +'_'+ ls[3]+'_' + ls[4] + "_ada.tif"
        f_temp = '/home/previ/raster_source/ada/3857/'+bname[0:-4] + '_tmp.tif'
        # for i in [f_2154,f_3857,f_temp]:
            # if (os.path.exists(i)):
                # os.remove(i)
        
        subprocess_wrapper.warp([f,f_temp,'-t_srs','EPSG:3857', '-co','COMPRESS=DEFLATE','--config','GDAL_CACHEMAX','512','-cutline','/home/previ/vector_source/bbox_aura_3857.shp','-crop_to_cutline','-ot','float32','-overwrite'])
        msg2154=subprocess_wrapper.warp([f,f_2154, '-co','COMPRESS=DEFLATE','--config','GDAL_CACHEMAX','512','-ot','float32','-dstnodata','-9999','-overwrite'])
        msg=subprocess_wrapper.warp([f_temp,f_3857, '-co','COMPRESS=DEFLATE','--config','GDAL_CACHEMAX','512','-cutline','/home/previ/vector_source/aura_reg_3857.shp','-crop_to_cutline','-tr', '1425', '1425','-ot','float32','-dstnodata','-9999','-overwrite'])

        #resamp(f_3857,f_3857_fine,14.25)
