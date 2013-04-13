import time
import soundfile
import arduino
import stream
import subprocess

import decimal
import datetime

import conversation


import MySQLdb

import calllog


valid_states = ("onhook", "dialtone", "middial", "afterdial", "incall","ringing", "stream", "capetalk", "busy", "playing", "comment", "closed", "pa")

f = open("/tmp/arduino","w")
class telephone():
	def __init__(self, id, name, ringerpinnum,onhookpinnum,channelnum, conversations, telephones, barqueue):
		self.name = name
		self.state = "ringing"
		
		#Onhook stuff
		try:
			int(onhookpinnum[1])
			self.digital = True
		except:
			self.digital = False

		self.onhooksince = self.gettime()		
		self.laststatesince = self.gettime()
		self.onhookstate = True
		self.globalringsince = 0
		
		self.barqueue = barqueue 
		
		self.id = id
		
		if onhookpinnum:
			if self.digital:
				self.onhookpin = arduino.boards[onhookpinnum[0]].get_pin('d:'+str(onhookpinnum[1])+':i', pinchangecallback = self.pinchangecallback)
			else:
				onhookpinnum[1] = onhookpinnum[1].replace('a','')
				self.onhookpin = arduino.boards[onhookpinnum[0]].get_pin('a:'+str(onhookpinnum[1])+':i', pinchangecallback = self.pinchangecallback)
			
			self.pinchangecallback()
			
		else:
			self.onhookpin = None
		
		
		
		#Ringer Stuff

		if ringerpinnum:
			self.ringerpin = arduino.boards[ringerpinnum[0]].get_pin('d:'+str(ringerpinnum[1])+':o')
		self.ringingsince = None # Not ringing
		self.ringerstate = True # Off
		
		self.numberdialled = list()
		
		self.stream = None # not playing the stream
		self.conversations = conversations # A list of all conversations
		
		self.channelnum = channelnum
		self.telephones = telephones
		
		self.newstate('onhook') # Put the phone down
		
		self.commentfile = None
		
	def gettime(self):
		return decimal.Decimal(time.time())
	
	def run(self, bufsize):
		if self.id == 7 and len(self.barqueue):  
			if self.state == 'onhook':
				print "Linking bar:"
				calleenum = self.barqueue[0]
				self.barqueue.pop()
				print "Barqueue is now %s" % self.barqueue
				new = conversation.conversation()
				new.invite(self)
				new.forceinvite(self.telephones[calleenum])
				self.conversations.append(new)
			else: 
				print "off hook"
		
		#self.onhook() 
		if not self.onhookpin:
			return 
			
		# Has the receiver been placed on hook
		if self.onhookstate and self.onhooksince < self.gettime()-decimal.Decimal(0.4) and not self.state in ('onhook','ringing'):
			print "Telephone %s has been on the receiver for some time (%f)." % (self.name, self.gettime() - self.onhooksince)
			self.newstate('onhook')
			
		# Is the phone in middial
		if self.state in ('middial') and self.onhookstate == False and self.onhooksince < self.gettime()-decimal.Decimal(0.2):
			self.newstate('afterdial')	

		# Has the phone been left off the hook?
		if self.state != 'onhook' and self.onhooksince < self.gettime()-decimal.Decimal(300):
			print "Telephone %s is stale." % (self.name)
			self.newstate('onhook')
			
			
		
		if self.state == 'afterdial' and self.number(): 
			out = self.number()			
			if len(out) == 10 and out[0] == '0': 
				# Connect to database
				conn = MySQLdb.connect(host="localhost",user="root",passwd="AZXCDxx",db="strand")
				cursor = conn.cursor()
				cursor.execute ("SELECT count(*) FROM cellnumber WHERE cellnumber_uid = %s", out)
				row = cursor.fetchone()
				if row[0]:
					self.addplay(soundfile.alreadycaptured,True)
					
				else: 
					cursor.execute("INSERT INTO cellnumber (cellnumber_uid, date) VALUES (%s, NOW())", out)
					self.addplay(soundfile.numcaptured,True)
					
				try:
					print "Sending SMS"
					import bulksms
					bulksms.sendsms_thread("27"+out[1:], "Alexander Bar loves you. Find us on Facebook & Twitter @AlexanderBarCt. And subscribe to www.alexanderbar.co.za/newsletter for specials & discounts.")
					print "Done sending SMS"
				except Exception, e:
					print repr(e)
					pass
					
				cursor.close ()
				conn.close ()
				self.numberdialled = list()
				
			if out == '1': 
				self.newstate('busy')
			if len(out) > 1 and out[0] == '2':
				if out == '222':
					self.newstate('stream', 'bbc')
				elif out== '223':
					self.newstate('stream', 'bbc4')					
				elif out== '224':
					self.newstate('stream', 'whatsplaying')
				elif out== '250':
					self.newstate('pa')
				elif out== '234':
					self.newstate('incall')
					self.addplay(soundfile.fullycommitted,True)
					
				elif out=='235':
					self.newstate('incall')
					self.addplay(soundfile.spinster,True)

				elif len(out) == 3:
					self.newstate('stream', str(out))
			if out == '3':
				self.newstate('busy')
			if out == '24': # Hear yourself
				new = conversation.conversation()
				new.forceinvite(self)
				self.conversations.append(new)
				self.newstate('incall')
			if int(out) >= 40 and int(out) <= 60:
				# Find phones
				for telephone in self.telephones:
					found = False
					if telephone.name == out:
						calleenum = telephone.id
						found = True
						break
				if not found:
					print "Could not find callee."
					self.newstate('busy')
				elif self.telephones[calleenum].state == 'incall':
					for myconversation in self.conversations:
						found = False
						for t in myconversation.partys:
							if t['telephone'].id == calleenum:
								found = True
						if found:
							for t in myconversation.partys:
								if t['telephone'].id != self.id:
									t['telephone'].addplay(soundfile.breakin, True)
									t['telephone'].addplay(None)
									
							myconversation.forceinvite(self) # Break in
							self.newstate('incall')
				
				elif self.telephones[calleenum].state in ['onhook']:
					new = conversation.conversation()
					new.invite(self.telephones[calleenum])
					new.forceinvite(self)
					self.conversations.append(new)
					self.newstate('incall')
				else: 
					print "Callee in state: "+ self.telephones[calleenum].state 
					self.newstate('busy')
	
			if out == '9':
				if self.id != 7:
					# Add to bar queue
					self.barqueue.append(self.id)
					self.addplay(soundfile.connectingtobar, True)
					self.newstate('playing')
					print "Added %s to bar queue %s" % (self.id, self.barqueue)
				else: 
					self.newstate('busy')
				
			if out == '7':
				self.newstate('incall')
				self.addplay(soundfile.directory,True)
				
			
			if out == '8':
				self.addplay(soundfile.leavecomment,True)
				self.addplay(None)
				self.newstate('comment')
				
			
		self.ringer() # Control the LED
		return self.play(bufsize) # Play soundfiles.
	
	def pinchangecallback(self):
		#if self.gettime() - self.onhooksince < 0.01:
		#	return
		if self.digital:
			newstate = self.onhookpin.read()
			#print "New state of telephone id "+str(self.id)+" is "+str(newstate)	
			if not newstate:
				newstate = False
			else: 
				newstate = True
			#if self.id == 7:
			#	newstate = not newstate 
				#print "Switching state for "+str(self.id)
		else:
			newstate = self.onhookpin.read()
			#	print "Analog read: "+str(newstate)
			#print "New state of telephone id "+str(self.id)+" is "+str(newstate)	
			if newstate > 0.6:
				newstate = True
			elif newstate < 0.4:
				newstate = False
			else: 
				return
		

		if self.onhookstate != newstate:
			if self.gettime() - self.onhooksince > 0.01:
				self.onhooksince = self.gettime()
				self.onhookstate = newstate
				self.onhookchange()
			
	def onhookchange(self):
		print "The onhook state of "+str(self.id)+" has changed to: "+str(self.onhookstate)
		if self.state == 'onhook' and self.onhookstate == False:
			if False and str(datetime.datetime.today().strftime("%H%M")) > "0300" and str(datetime.datetime.today().strftime("%H%M")) < "0600":
				self.newstate('closed')
			else: 
				self.newstate('dialtone')
			
		if self.state in ('dialtone', 'afterdial') and self.onhookstate == True:
			self.numberdialled.append(0)
			print "number so far "+str(self.numberdialled)
			self.newstate('middial')
		if self.state in ('middial') and self.onhookstate == False:
			self.numberdialled[-1] += 1
			print "number so far "+self.number() 
			if self.number():
				self.addplay(soundfile.numbers[int(self.number() [-1])], True)
				self.addplay(None)
			else: 
				self.newstate('dialtone')
		if self.state == 'ringing' and self.onhookstate == False:
			self.newstate('incall')
		
			
	
	def newstate(self,state,param1=None):
		if state == self.state: return
		
		
		duration = float(self.gettime()) - float(self.laststatesince)
		self.laststatesince = self.gettime()
		print "duration", duration
		if duration > 1:
			calllog.calllog(self.id, self.number(), duration ,self.state)
				
		
		if state not in valid_states:
			raise Exception(state+" is not a valid state.")
			
		# Old states
		if self.state in ('stream'): 
			self.stream.__del__()
			self.stream = None
			
		if self.state == 'comment':
			self.commentfile.close()
			# Now email someone
		
		
		
		self.onhooksince = self.gettime()		
		
		# Change state
		self.state = state
		
		# New states
		print self.name+" is in state: "+self.state
		if self.state in ('onhook', 'dialtone'):
			self.numberdialled = list()
		
		if self.state == 'dialtone':
			self.addplay(soundfile.welcome, True)
			
		if self.state == 'busy':
			self.addplay(soundfile.busy, True)
			
		if self.state == 'onhook':
			self.addplay(None, True)
			
		if self.state == 'stream':
			self.addplay(None, True)
			self.stream = stream.stream(streamname=param1)
			
		if self.state == 'incall':
			self.addplay(None, True)
		
		if self.state == 'ringing':
			self.addplay(soundfile.buzz, True)
			#self.addplay(soundfile.telephonering, True)
			#subprocess.check_call(['/bin/bash','-c','/usr/bin/lynx -source http://pos.nitric.co.za/ring.php > /dev/null &'])
			
		if self.state == 'comment':
			self.addplay(soundfile.leavecomment, True)
			self.addplay(None)
			self.commentfile = open("comments/"+str(self.id)+"_"+str(time.time())+".raw", "w")
			print "Saving comments to file."
			
		if self.state == 'closed':
			self.addplay(None, True)
			self.addplay(soundfile.goodbye, True)
			
	def ringer(self):
		"""Blink the ringer if necessary"""
		if self.id == 7 and self.state == 'ringing' and self.globalringsince < self.gettime()-decimal.Decimal(7): 
			subprocess.check_call(['/bin/bash','-c','/usr/bin/lynx -source http://pos.nitric.co.za/ring.php > /dev/null &'])
			self.globalringsince = self.gettime()
			
			
		if self.state == 'ringing':
			if not self.ringingsince:
				self.ringingsince = self.gettime() # Start the timer
				
			if self.ringingsince < self.gettime()-decimal.Decimal(0.25): # Toggle pins, and reset timer
				self.ringerstate = not self.ringerstate
				self.ringingsince = self.gettime()
				#print "Writing "+str(self.ringerstate)
				self.ringerpin.write(self.ringerstate)
				

		elif self.state in ('onhook',):
			if self.ringerstate: # If not ringing, make sure the light is off
				self.ringerstate = False
				self.ringerpin.write(self.ringerstate)
				self.ringingsince = None
		
		elif self.state == 'middial':
			if self.ringerstate != self.onhookstate:
				self.ringerstate = self.onhookstate
				self.ringerpin.write(self.ringerstate)
		
		else:
			self.ringerstate = True
			self.ringingsince = self.gettime()
			self.ringerpin.write(self.ringerstate)
	
	def number(self):
		out = ""
		if self.state == 'afterdial' and len(self.numberdialled) > 0 and self.numberdialled[0] == 1:
			self.numberdialled = self.numberdialled[1:] # We don't allow the number 1 at the beginning of a number.
		
		for x in self.numberdialled:
			if x >= 10:
				out += "0"
			else: 
				out += str(x)
		
		return out
		
	
	def addplay(self, soundfile, interrupt=False):
		if interrupt:
			self.playing = list()
			self.playingpos = 0
		if soundfile:
			print self.name+" Added "+soundfile.filename
			self.playing.append(soundfile)
		else:
			self.playing.append(None)
			
	
	def play(self, bufsize):
		if self.state in ('stream'):
			output = self.stream.getsomestream(bufsize)
			return output		
		elif len(self.playing) > 1 and self.playing[0] == None:
			self.playing = self.playing[1:]
		elif len(self.playing) and self.playing[0] != None:
			# copy bufsize of stuff to "channel" the output buffer
			output, nextposition = self.playing[0].playsegment(self.playingpos, bufsize)
			self.playingpos = nextposition
			
			if nextposition == 0:
				if len(self.playing) > 1:
					self.playing = self.playing[1:]				
			
			return output
			
		
		else:
			return None

	def savecommentbuffer(self, buffer):
		if self.commentfile:
			self.commentfile.write(buffer)
		
