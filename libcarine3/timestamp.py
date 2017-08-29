### on va tout faire en timestamp
# ca evite de manipuler des dates en permanence
# getSec renvoie le nb de sec passées entre minuit et la commande
# getTimestamp renvoie le timestamp du jour demandé :
# delta | jour
#   0   | aujourd'hui
#   1   | hier
#   2   | avant-hier
#   3   | hmmmm ?

import datetime
import time


def getSec():
    d=datetime.datetime.now()
    sec=(d.hour*3600)+(d.minute*60) + d.second
    return sec
    
def getTimestamp(delta):
    sec_jour=3600*24
    sec=getSec()
    tsp=int(time.time()-sec-(sec_jour*delta))
    return tsp
