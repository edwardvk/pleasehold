import onlyoneprocess
onlyoneprocess.onlyoneprocess("pleasehold")

import time
import jack
import soundfile
import arduino
import telephone
import numpy
import conversation
import socket


import gobject
gobject.threads_init()

print "Connecting to jackd"
jack.attach("pleasehold")
# All sound works via jackd -- so if you want multiple sound cards, then glue them together with ALSA

from tempfile import TemporaryFile
outfile = TemporaryFile()


conversations = list()
telephones = list()
barqueue = list()

phonemap = ['44','41','50','58','56','54','51','9','57','43','40','53','52','55','59']

if not "rose" in open("/etc/hostname").read():
	channels = 15
	
	telephones.append(telephone.telephone(0, phonemap[0], ringerpinnum=(1,4),onhookpinnum=[1,'12'],channelnum=0, conversations=conversations, telephones=telephones,barqueue=barqueue))	
	telephones.append(telephone.telephone(1, phonemap[1], ringerpinnum=(1,3),onhookpinnum=[1,'11'],channelnum=1, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(2, phonemap[2], ringerpinnum=(1,2),onhookpinnum=[1,'10'],channelnum=2, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(3, phonemap[3], ringerpinnum=(1,7),onhookpinnum=[1,'a2'],channelnum=3, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(4, phonemap[4], ringerpinnum=(1,9),onhookpinnum=[1,'a4'],channelnum=4, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(5, phonemap[5], ringerpinnum=(1,5),onhookpinnum=[1,'a0'],channelnum=5, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(6, phonemap[6], ringerpinnum=(1,8),onhookpinnum=[1,'a3'],channelnum=6, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(7, phonemap[7], ringerpinnum=(1,6),onhookpinnum=[1,'a1'],channelnum=7, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(8, phonemap[8], ringerpinnum=(0,8),onhookpinnum=[0,'a3'],channelnum=8, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(9, phonemap[9], ringerpinnum=(0,9),onhookpinnum=[0,'a4'],channelnum=9, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(10, phonemap[10], ringerpinnum=(0,2),onhookpinnum=[0,'10'],channelnum=10, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(11, phonemap[11], ringerpinnum=(0,3),onhookpinnum=[0,'11'],channelnum=11, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(12, phonemap[12], ringerpinnum=(0,4),onhookpinnum=[0,'12'],channelnum=12, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(13, phonemap[13], ringerpinnum=(0,5),onhookpinnum=[0,'a0'],channelnum=13, conversations=conversations, telephones=telephones,barqueue=barqueue))
	telephones.append(telephone.telephone(14, phonemap[14], ringerpinnum=(0,6),onhookpinnum=[0,'a1'],channelnum=14, conversations=conversations, telephones=telephones,barqueue=barqueue))
	#telephones.append(telephone.telephone(15, phonemap[15], ringerpinnum=(0,7),onhookpinnum=[0,'a2'],channelnum=15, conversations=conversations, telephones=telephones,barqueue=barqueue))

else:
	channels = 2
	telephones.append(telephone.telephone(0, "Phone 52", ringerpinnum=None,onhookpinnum=None,channelnum=0,conversations= conversations, telephones=telephones))
	telephones.append(telephone.telephone(1, "Phone 53", ringerpinnum=None,onhookpinnum=None,channelnum=1,conversations= conversations, telephones=telephones))


print "There are %d phones." % (len(telephones))

for x in range(channels):
	num = str(x+1)
	jack.register_port("out_"+num, jack.IsOutput)
	jack.register_port("in_"+num, jack.IsInput)

jack.activate()

num_telephones = channels # Create 8 telephones for now

for x in range(num_telephones):  
	num = str(x+1)
	if x < 8:
		jack.connect("system:capture_"+num, "pleasehold:in_"+num)
		jack.connect("pleasehold:out_"+num, "system:playback_"+num)
	else:
		alsa_num = str(x-7)
		jack.connect("alsa_in:capture_"+alsa_num, "pleasehold:in_"+num)
		jack.connect("pleasehold:out_"+num, "alsa_out:playback_"+alsa_num)


bufsize = jack.get_buffer_size()

samplerate = float(jack.get_sample_rate())
print "jackd: ", channels, "buffersize", bufsize, "samplerate", samplerate

headphones = numpy.zeros((channels,bufsize), 'f')
microphones = numpy.zeros((channels,bufsize), 'f')

# Testing 
debug = 0
sock = None
#new = conversation.conversation()
#new.forceinvite(telephones[2])
#conversations.append(new)
ringposition = 0
nextringposition = ringposition

while(True): # Main Loop
	if (debug): print "Process in/out with jack"	
	try:
		jack.process(headphones, microphones)
	except jack.InputSyncError, e:
		print repr(e)
	except jack.OutputSyncError, e:
		print repr(e)

	if (debug): print "Splitting"	
	micsplit = numpy.vsplit(microphones,channels)
	
	out = list()
	for x in range(channels):
		out.append([numpy.zeros((1,bufsize),'f')])
		
	if (debug): print "Run telephone sounds"	
	pamode = False
	for telephone in telephones:
		thisphone = telephone.run(bufsize) # Play sounds, control LED, change states		
		if thisphone != None: # The telephone is playing it's own sound.
			out[telephone.channelnum].append(thisphone)
			
		if telephone.state == 'comment':			
			telephone.savecommentbuffer(micsplit[telephone.id])
			
		if telephone.state == 'pa':
			if not sock:
				try: 
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect(('pos.nitric.co.za', 9999))
				except:
					pass
			outfile.seek(0)
			(micsplit[telephone.id]/2).tofile(outfile)
			outfile.seek(0)
			string = outfile.read(8*1024)
			try:
				sock.sendall(string)				
				pamode = True
			except socket.error: 
				pass
				

			
		if not telephone.digital:
			telephone.pinchangecallback()


	if sock and not pamode: 
		sock.close()
		sock = None
		

	# Add the conversations
	if (debug): print "Adding conversations"	
	for conversation in conversations:
		ringing = conversation.isringing()
		for partyA in conversation.partys:
			if conversation.allringing() or partyA['telephone'].state in ('onhook'):
				conversation.hangup(partyA['telephone'])
				
			for partyB in conversation.partys:
				if partyA['telephone'].id != partyB['telephone'].id or len(conversation.partys) == 1:
					if partyA['telephone'].state == 'incall' and partyB['telephone'].state == 'incall':
						out[partyA['telephone'].id].append(micsplit[partyB['telephone'].id])
						
			if ringing and partyA['telephone'].state == 'incall' and not 7 in conversation.partys:
				output, nextringposition = soundfile.ringring.playsegment(ringposition, bufsize)				
				out[partyA['telephone'].id].append(output)
				
	ringposition = nextringposition
				
	# Blend the outputs
	if (debug): print "Blending outputs"
	for x in range(channels):		
		count = len(out[x])
		if count == 1:
			out[x] = out[x][0] # Straight out
		if count > 1:
			newout = out[x][0]
			for y in range(1, count):
				newout = numpy.add(newout, out[x][y]) # Merge 
			out[x] = newout
			out[x] /= count
		else: 
			out[x] = numpy.zeros((1,bufsize),'f') # Quiet
		
		
	
	headphones = numpy.array(numpy.vstack(out),'f')
	
	if (debug): print "Checking bytes available arduinos"
	
	for board in arduino.boards:
		while board.bytes_available():
			try:
				board.iterate()
			except Exception, e:
				print "Exception: ", repr(e)
	
	if (debug): print "Checking pinchangecallback"
	for telephone in telephones:
		telephone.pinchangecallback()
	

