import threading
import time
import serial

import pyfirmata



# remove the port used by the arduino
removeport1 = open("/tmp/dooropener_arduino", "r").read().strip()
removeport2 = open("/tmp/dooropener_arduino2", "r").read().strip()

# Looking for arduino
ports = []
for i in range(0,10):
	port = '/dev/ttyACM'+str(i)
	if removeport1 != port and removeport2 != port:
		ports.append(port) # Ports /dev/ttyACM0 -> /dev/ttyACM10
	else:
		print "Ignoring "+str(port)+" because it is assigned to door control system."

arduinos = 2
boards = []


for port in ports:
	#if port == '/dev/ttyACM2': continue
	try: 
		print "Trying port", port 
		b = pyfirmata.Board(port, pyfirmata.boards.BOARDS['arduino'])
	
		print "Success connecting to", port
		
		boards.append(b)	

		print "Found an arduino %s" % len(boards)			
		if len(boards) >= arduinos:
			break

	except Exception, e: 
		print "Failure to connect to", port, e
		

while(len(boards) < arduinos):
	class pin():
		def write(self, x): pass
		def read(self): return 1
	class arduinosimulator():
		def get_pin(self, x, pinchangecallback=None): return pin()
		def bytes_available(self): return None
		def init(self): return None
		def get_firmata_version(self): return "Fake"
		analog = {}
		digital = {}
		
		
		def __init__(self):
			for x in range(10):
				self.analog[x] = pin()
				self.digital[x] = pin()
	
	boards.append(arduinosimulator())

	print "Fake Arduino's Ready"


print "Waiting for arduino's to auto-reset"
boards[0].pass_time(5)

pins = []
for board in boards:
	board.init()
	firmata_version = board.get_firmata_version()	
	print "Firmata version: "+str(firmata_version)
	pins.append(board.get_pin("a:5:i"))
	while board.bytes_available():
		board.iterate()	


while(True):
	success = True
	for pin in pins: 
		x = pin.read()
		#print pin, x
		if  x == None:
			success = False
			break
	if success:
		break
	for board in boards:
		while board.bytes_available():
			board.iterate()

if pins[0].read() > 0.8:
	# swap. 
	print "Swapping..."
	board = boards[0]
	boards[0] = boards[1]
	boards[1] = board

print "Board 0", boards[0].analog[5].read()
print "Board 1", boards[1].analog[5].read()

if boards[0].get_firmata_version() != "Fake":
	assert boards[0].analog[5].read() < 0.8
if boards[1].get_firmata_version() != "Fake":
	assert boards[1].analog[5].read() > 0.8

print "Real Arduino's Ready"
	

	



if __name__ == "__main__":
	while(True):
		#print pina0.read(), pin10.read(), pin11.read()
		x = 0
		for pin in pins: 
			x += 1
			print x, pin, pin.read()
			
		
		for board in boards:
			while board.bytes_available():
				board.iterate()
	
		time.sleep(0.001)
