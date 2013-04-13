class conversation():
	def __init__(self):
		self.partys = list() # No callers. Each caller is {'telephone': X, 'state': X} where state can be 'ringing', 'inprogress'
		
	def invite(self, telephone):
		telephone.newstate('ringing')
		self.partys.append({'telephone': telephone})
		self.show()
		
	def hangup(self, telephone):
		todel = list()
		for x in range(len(self.partys)):
			if self.partys[x]['telephone'].id == telephone.id:
				print "Removing %s from the conversation." % (self.partys[x]['telephone'].id)
				todel.append(x)
				telephone.newstate('onhook')
		
		
			
		for x in todel:
			del(self.partys[x])
		
		# If there is only 1 person left now, then hang them up too
		if len(self.partys) == 1:
			self.partys[0]['telephone'].newstate('onhook')
			self.partys = list()

		self.show()		
		
	def forceinvite(self, telephone):
		if telephone.id != 7:
			telephone.newstate('incall')
		self.partys.append({'telephone': telephone})
		self.show()
		
	def isringing(self):
		for x in self.partys:
			if x['telephone'].state == 'ringing':
				return True
		return False
		
	def allringing(self):
		for x in self.partys:
			if x['telephone'].state != 'ringing':
				return False
		return True


	def show(self):
		print "Conversation: "+str(list(x['telephone'].id for x in self.partys))