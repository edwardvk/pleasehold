import os


def onlyoneprocess(token):
	filename = "/var/run/load."+token+".py.pid"
	#determine permissions
	try:
		open(filename, "a")
	except IOError: 
		#Alright, use /tmp then
		filename = "/tmp/load."+token+".py.pid"
		
	if os.path.exists(filename):
		try:
			oldpid = int(open(filename, "r").read())
		except ValueError:
			oldpid = -1
		if os.path.exists("/proc/"+str(oldpid)):
			print "Another process is already running: %d" % oldpid
			exit(1)
		
	f = open(filename, "w")
	f.write(str(os.getpid()))
	f.close()


if __name__ == "__main__":
	onlyoneprocess("test")