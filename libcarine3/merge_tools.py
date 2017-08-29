import numpy as np
import config
import rasterio as rio
def merge_method(m,arrs):
    m_auth=['max']
    if (m not in m_auth):
        print('method inconnue, peut rien faire.... try again')
    else:
        new_arr=np.zeros(arrs[0].shape)
        for i in arrs:
            new_arr=np.maximum(new_arr,i)
        return new_arr
        
def sous_indice(arr,poll):
    ALE=config.ALE[poll]
    INFO=config.VLS[poll]
    data=(arr<(INFO/5))*((arr*10)/(INFO/5))+((arr>=(INFO/5))*(arr<=INFO))*(((arr*100)/INFO)-10)+(arr>INFO)*(90+(arr-INFO)*10/(ALE-INFO))
    return data   
# Si [P]< INFOP/5 : Ip = 10*[P]/( INFOP/5) 
# •Si [P] ≤ INFOP : IP = ([P]*100/INFOP) -10
# •Si [P] ≤ INFOP : IP = ([P]*100/INFOP) -10
# •Si [P] > INFOP : IP = 90+([P]-INFOP)*10/(ALEP-INFOP) 
def rasterize(poly, rstshape, rstaff):

    shapes = ((g, 1) for g in [poly])
    rbuf = features.rasterize(shapes=shapes,
                              out_shape=rstshape,
                              transform=rstaff,
                              all_touched=True)
    return rstshape