#genere l'archive quotidienne de carine
import urllib.request
import sys


def main(tsp=None):

	if (tsp==[]):
		tsp = 0
		res=urllib.request.urlopen(r'http://localhost/carinev3/raster/zipday?tsp='+str(tsp))
		print(tsp)
		return res
		
if __name__ == "__main__":
	print(sys.argv)
	main(sys.argv[1:])