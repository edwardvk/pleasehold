import socket
import StringIO
import urllib
import urllib2
import pprint as prettyprinter
import setpath
import settings

import time
from threading import Thread

username = settings.bulksmsusername
password = settings.bulksmspassword
server = settings.bulksmsserver
port = settings.bulksmsport
url_submission = settings.bulksmsurl


def sendsms(number, text):
	"""Send an SMS to the number given and return true is successfully submitted."""
	print "Starting sendsms for %s with text %s" % (number, text)
	number = str(number)
	
	if len(text) > 160: 
		text = text[0:157]+"..." #Add ellipses if too long.
	if number[0] == "0": 
		number = "27"+number[1:] #Assume South Africa prefix
	if number[0] == "+":
		number = number[1:] #Bulksms does not want the +
	if number[0:-1] == "2783000000":
		return True #Test case
	number = str(number).strip()
	
	param = {
		'message': text,
		'username': username,
		'password': password,
		'msisdn': number
	}
	result = post("http://"+server+":"+port+url_submission,param)
	response = result.split("|")
	code = response[0] 
	comment = response[1]
	
	if code != '0':
		raise Exception(response)
	
	return True
	

def post(url, param = None):
	url = url
	#print "Posting",url,param
	
	data = ""

	if param:
		data = urllib.urlencode(param)

	try:
		req = urllib2.Request(url, data)
		response = urllib2.urlopen(req)
		result = response.read()
	except urllib2.URLError, e:
		print e.code
		print e.read()
		raise Exception("Cannot send SMS")
	
	return result

def get(url, param = None):
	return post(url, param) #@TODO


def pprint(desc, struct):
	print '------------------------------------------'
	print desc
	print prettyprinter.pformat(struct)
	print '------------------------------------------'




def sendsms_thread(*a, **kw):
	print "Now starting thread for sms: "+repr(a)+" "+repr(kw)
	t = Thread(target=sendsms, args=a, kwargs=kw)
	t.start()


if __name__ == '__main__':
	#Sending Test
	print sendsms_thread("27836456443 ","Hello");
	print "Done"

