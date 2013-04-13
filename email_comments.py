import glob
import subprocess
import emailer
import os

files = glob.glob('comments/*.raw')
for file in files:
	newfile = file.replace(".raw",".ogg")
	subprocess.check_call(["sox","-r","44.1k","-e","float","-b","32","-c","1",file,newfile])
	telephoneid = "5"+newfile.split("_")[0].split("/")[-1]
	emailer.send("comments@alexanderbar.co.za", "Alexander Bar Telephone System <comments@alexanderbar.co.za>", "Comment from Telephone %s" % (telephoneid),"Test", html="Hi",attachments=[(newfile,"audio/ogg")])
	os.unlink(file)
	os.unlink(newfile)




#
 