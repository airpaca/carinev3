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
from time import gmtime, strftime
from datetime import timedelta,date


def getSec():
    d=datetime.datetime.now()
    sec=datetime.datetime.now()-(d.hour*3600)+(d.minute*60) + d.second
    return sec
    
def getTimestamp(delta):
    n=datetime.datetime.now()
    m=n.month
    y=n.year
    d=n.day

    date = datetime.date(y,m,d)
    dt = timedelta(days = delta)
    date=date-dt
    
    #print(date)
    tt=date.timetuple()
    #print(tt)
    
    tsp = int(time.mktime(tt))
    return tsp

def getTimestampFromDate(date):
    y=int(date[0:4])
    m=int(date[4:6])
    d=int(date[6:8])
    date = datetime.date(y,m,d)
    #print(date)
    tt=date.timetuple()
    #print(tt)
    tsp = int(time.mktime(tt))
    return tsp