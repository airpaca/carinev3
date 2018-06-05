import os
import time

def checkfile(f,duree):
# duree en secondes
    if (os.path.exists(f)):
        delai= time.time()-os.stat(f)[7]
        if (delai >  duree):
            return True
        else :
            return False
    else :
        return False
    