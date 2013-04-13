import numpy
from scipy.io import wavfile
from scipy.signal import resample
import scipy
import os


class soundfile():
	def __init__(self, filename): 
		self.filename = os.path.basename(filename)
		if filename[-4:].lower() == ".wav":
			print "Loading "+filename
			self.samplerate, self.audio = wavfile.read(filename)
			self.audio = numpy.array(self.audio, 'f')
		else:
			raise Exception("Sound file now supported: "+str(filename))
		self.audio /= numpy.max(numpy.abs(self.audio),axis=0)
			
		# Load the file, and convert to 44100 Hz
		if self.samplerate != 44100:
			print "Resampling: "+self.filename
			duration = len(self.audio)/float(self.samplerate)
			bufsize = round(duration*44100)
			self.audio = resample(self.audio, bufsize)
		
	def replacedata(self, data):
		self.audio = data
		
	def playsegment(self, position, bufsize):
		output = self.audio[position:position+bufsize].transpose()
		if len(output) < bufsize: # Pad with zeroes if necessary
			output = numpy.hstack((output, numpy.zeros(bufsize - len(output))))
		nextposition = position + bufsize
		if nextposition > len(self.audio):
			nextposition = 0
		return (output, nextposition)
		
	
	def __str__(self):
		return "Audio %s Length: %s Samplerate: %s" % (self.filename, len(self.audio), self.samplerate)
	
	
welcome = soundfile("wavs/welcome.wav")
dialtone = soundfile("wavs/dialtone.wav")
busy = soundfile("wavs/busy.wav")
connectingtobar = soundfile("wavs/connectingtobar.wav")
illusion = soundfile("wavs/illusion.wav")
ringring = soundfile("wavs/ringring.wav")
buzz = soundfile("wavs/buzz.wav")
breakin = soundfile("wavs/breakin.wav")
leavecomment = soundfile("wavs/leavecomment.wav")
goodbye = soundfile("wavs/goodbye.wav")
numcaptured = soundfile("wavs/numcaptured.wav")
alreadycaptured = soundfile("wavs/alreadycaptured.wav")
telephonering = soundfile("wavs/telephonering.wav")
directory = soundfile("wavs/directory.wav")
fullycommitted = soundfile("wavs/fullycommitted.wav")
spinster = soundfile("wavs/spinster.wav")

numbers = dict()
for x in range(10):
	numbers[x] = soundfile('wavs/%s.wav' % (x,))

if __name__ == "__main__":
	print welcome
	print numbers[0]
	print dialtone
	print (dialtone.playsegment(0, 1024))
	print (connectingtobar.playsegment(0,1024))
	print leavecomment
