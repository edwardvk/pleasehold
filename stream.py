import gst
import numpy
import scipy.signal

import Queue
import gobject
gobject.threads_init()

class stream:
	def __init__(self, streamname='bbc'):
		self.pipeline = None
		self.streamname = streamname
		streams = {
			'bbc': 'http://bbcwssc.ic.llnwd.net/stream/bbcwssc_mp1_ws-eieuk',
			'bbc4': "http://wm-live.bbc.net.uk/wms/bbc_ami/radio4/radio4_bb_live_int_ep1_sl0?BBC-UID=b4adbcdf5ba7eea337440a77610973cee5bd1676f0b0524162a83074f35cc068",
			'test': 'rtmp://216.246.37.52/fmr',
			'capetalk': 'mms://46.4.25.237/capetalk-live',
			'whatsplaying': 'http://pos.nitric.co.za/whatsplaying',
			'npr': 'http://69.166.45.60/nwpr'
		}
		
		
		url = streams.get(streamname,"http://pos.nitric.co.za/twohundred/s"+streamname)
		print "Starting stream pipeline: "+url
		self.pipeline = gst.parse_launch('''
		souphttpsrc location="%s" !
		decodebin ! audio/x-raw-int !
		appsink name=sink sync=False''' % url)
		#http://mp32.bbc.streamuk.com:80/
		#mms://a243.l3944038972.c39440.g.lm.akamaistream.net/D/243/39440/v0001/reflector:38972
		self.sink = self.pipeline.get_by_name('sink')
		self.pipeline.set_state(gst.STATE_PLAYING)
		
		self.sink.connect('new-buffer', self.on_new_buffer)
		self.sink.set_property('emit-signals', True)

		self.streamrate = 22050.0 # Hz
		
		if streamname=='220':
			self.streamrate = 88200 # Hz
		
		self.bufsize = 576
		
		self.buffer = numpy.zeros(1024) 
		self.queue = Queue.Queue()
		
	def __del__(self):
		self.sink.set_property('emit-signals', False)
		self.pipeline.set_state(gst.STATE_PAUSED)
		self.queue = None
		self.pipeline = None
		
		
	def on_new_buffer(self, buf):
		buf = self.sink.emit('pull-buffer')
		self.queue.put(buf.data)
		#print len(numpy.array(numpy.fromstring(buf.data, dtype=numpy.int16),'f')/16048)
		
		
	def getsomestream(self, bufsize):
		#return numpy.zeros(1024) 
		
		seconds = float(bufsize)/44100.0
		datatoget = seconds*self.streamrate
		
		#print "Queue size: ", self.queue.qsize()
		try: 
			self.buffer = numpy.hstack((self.buffer,numpy.array(numpy.fromstring(self.queue.get_nowait(), dtype=numpy.int16),'f')/16048))
			self.queue.task_done()
		except Queue.Empty: 
			pass
			
			
		
		#print "Buffer size", len(self.buffer)
		if len(self.buffer) >= datatoget:			
			#print "Not waiting"
			output = self.buffer[:datatoget]
			self.buffer = self.buffer[datatoget:]
			n = numpy.array(scipy.signal.resample(output, bufsize),'f')
			return n
			return numpy.zeros(1024) 
		else: 			
			print "Waiting for stream: "+self.streamname
			return numpy.zeros(1024) 
	
		

	

	
