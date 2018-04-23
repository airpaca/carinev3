from raster.models import Polluant
import subprocess
import os
import config
from libcarine3 import write_log
def gdaldem(fic1,fic2):

    #new_name=fic.replace('_','-')
    colormap_file='/var/www/html/carinev3/libcarine3/colormaps/normalize_colors.txt'
    # gdaldem color-relief slope.tif color-slope.txt slope-shade.ti
    #write_log.append_log(new_name)
    #write_log.append_log(colormap_file)
    options=['gdaldem','color-relief',fic1,colormap_file,fic2,'-co','compress=DEFLATE','-co','TILED=YES','-alpha','--config','GDAL_CACHEMAX','8192','-nearest_color_entry']   
    
    #options.extend(argz)
    a=subprocess.call(options)   
    write_log.append_log(a)
    return  fic2
    
def scp(fic):
    
    msg=subprocess.call(['/var/www/html/carinev3/send_file.sh',os.path.basename(fic)])
    return msg   
    
def warp(argz):
    """with a def you can easily change your subprocess call"""
    # command construction with binary and options
    options = ['gdalwarp']
    options.extend(argz)
    # call gdalwarp 
    msg=subprocess.call(options)
    #write_log.append_log(str(msg))
    return msg

def scp_classic(fic,dest_host,dest_user,dest_dir):
    #fic = source fullname
    bname=os.path.basename(fic)
    #dest rep
    dest=dest_user + "@" + dest_host + ":" + os.path.join(dest_dir,bname)
    msg=subprocess.call(['scp','-r','-p',fic,dest])
    return msg


def fake(fic):
    msg=subprocess.call(['/var/www/html/carinev3/send_file.sh',os.path.basename(fic)])
    return msg