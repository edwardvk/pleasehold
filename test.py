import numpy
import jack
import stream
import time
import copy


print "Connecting to jackd"
print "Don't forget to run:  jackd -d alsa -d hw:M1010LT -r 44100 "
print "Or:  jackd -d alsa -r 44100 "
jack.attach("pleasehold")

channels = 2
for x in range(channels):
	num = str(x+1)
	jack.register_port("out_"+num, jack.IsOutput)
	jack.register_port("in_"+num, jack.IsInput)

jack.activate()

for x in range(channels):  
	num = str(x+1)
	jack.connect("system:capture_"+num, "pleasehold:in_"+num)
	jack.connect("pleasehold:out_"+num, "system:playback_"+num)

bufsize = jack.get_buffer_size()
samplerate = float(jack.get_sample_rate())

headphones = numpy.zeros((channels,bufsize), 'f')
microphones = numpy.zeros((channels,bufsize), 'f')

b = None

loop = 0 




while(True): # Main Loop
	loop += 1
	#print loop
	try:
		jack.process(headphones, microphones)
	except jack.InputSyncError, e:
		print repr(e)
	except jack.OutputSyncError, e:
		print repr(e)


	micsplit = numpy.vsplit(microphones,channels)
	
	out = list()
	for x in range(channels):
		out.append([numpy.zeros((1,bufsize),'f')])
		
	
	if loop > 10:
		if not b: 
			#b = capetalk.capetalk()
			b = stream.stream('220')
		data = b.getsomestream(bufsize)
		out[1].append(data)
		out[0].append(data)	
	else: 
		out[0].append(micsplit[0])
	
	
	out[1].append(micsplit[0])
	
	# Blend the outputs
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
