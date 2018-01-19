import os
import carinev3.settings as sets
import config
import datetime
def append_log(msg):
    if (sets.DEBUG == True):
        d=datetime.datetime.now().strftime("%d/%m/%y %H:%M")
        fic = open(config.mylogs,'a')
        fic.write(str(d) + " : " + str(msg) + "\n")
        fic.close()
    return
    