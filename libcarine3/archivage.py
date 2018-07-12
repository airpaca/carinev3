#!/usr/bin/env python
import os
import zipfile

def zipdir(outfile,urlss):
	print(urlss)
	with zipfile.ZipFile(outfile, 'w', zipfile.ZIP_DEFLATED) as zipf:
		for k in urlss.keys():
			print(k)
			for file in urlss[k]:
				if os.path.exists(file):
					print(os.path.join(k),os.path.basename(file))
					zipf.write(file,os.path.join(k,os.path.basename(file)))
				else :
					print("404 : " + file)

# if __name__ == '__main__':
	# zipf = zipfile.ZipFile('Python.zip', 'w', zipfile.ZIP_DEFLATED)
	# zipdir('tmp/', zipf)
	# zipf.close()