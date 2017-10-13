from raster.models import Polluant
import subprocess
import config
def gdaldem(fic):
    ls=fic.split('_')
    new_name=fic.replace('_','__')
    pol=ls[1].upper()
    p=Polluant.objects.get(nom=pol)
    print(p)   
    colormap_file='/var/www/html/carinev3/libcarine3/colormaps/normalize_colors.txt'
    # gdaldem color-relief slope.tif color-slope.txt slope-shade.ti
    options=['gdaldem','color-relief',fic,colormap_file,new_name,'-co','compress=DEFLATE','-co','TILED=YES','-alpha','--config','GDAL_CACHEMAX','16384','-nearest_color_entry']   
    print(options)
    #options.extend(argz)
    msg=subprocess.call(options)   
    return  new_name
    
def scp(fic):
    dest=config.hd_dest
    options=['scp','-p',fic,dest]
    msg=subprocess.call(options)
    return msg   
    
def warp(argz):
    """with a def you can easily change your subprocess call"""
    # command construction with binary and options
    options = ['gdalwarp']
    options.extend(argz)
    # call gdalwarp 
    msg=subprocess.check_call(options)
    return msg