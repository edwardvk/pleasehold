from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
import re


import smtplib
import uuid
import os


pytype=type


def send(mailto, mailfrom, subject, text=None, **kwargs):
	if isinstance(mailto, basestring):
		if ("," in mailto or ";" in mailto):
			mailto = re.split(r'\s*,\s*|\s*;\s*', mailto)
		else:
			mailto = [mailto]
	if kwargs.has_key('html'):
		html = kwargs['html']
	else:
		html = None
	if kwargs.has_key('images'):
		images = kwargs['images']
	else:
		images = []
	
	print images
	# me == my email address
	# you == recipient's email address
	me = "my@email.com"
	you = "your@email.com"
	
	rootmsg = MIMEMultipart()
	rootmsg['Subject'] = subject
	rootmsg['From'] = mailfrom
	rootmsg['To'] = ','.join(mailto)

	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart('alternative')
	rootmsg.attach(msg)
	
	# Record the MIME types of both parts - text/plain and text/html.
	if text:
		part1 = MIMEText(unicode(text).encode('utf-8'), 'plain', _charset='utf-8')
		msg.attach(part1)
	
	cids = {}
	
	#first make the cids
	for file in images:
		cids[os.path.basename(file)] = str(uuid.uuid1())
	
	
	if html:
		for k in cids:
			s1 = 'src="%s"' % k
			s2 = 'src="cid:%s"' % cids[k]
			html = html.replace(s1, s2)
			s1 = "url('%s')" % k
			s2 = "url('cid:%s')" % cids[k]
			html = html.replace(s1, s2)
			s1 = 'background="%s"' % k
			s2 = 'background="cid:%s"' % cids[k]
			html = html.replace(s1, s2)
		part2 = MIMEText(html, 'html', 'utf-8')
		msg.attach(part2)
	
	for file in images:
		fp = open(file, 'rb')
		img = MIMEImage(fp.read())
		img.add_header('Content-ID', '<'+cids[os.path.basename(file)]+'>')
		img.add_header('Content-Disposition', 'inline; filename="%s"' % os.path.basename(file))
		fp.close()
		rootmsg.attach(img)
	
	if kwargs.has_key('attachments'):
		for filename, type in kwargs['attachments']:
			t = type.split('/')
			if t=='text':
				a = MIMEText(open(filename).read(), _subtype=t[1])
			elif t=='image':
				a = MIMEImage(open(filename).read(), _subtype=t[1])
			else:
				a = MIMEBase(t[0], t[1])
				a.set_payload(open(filename, "rb").read())
				encoders.encode_base64(a)

			a.add_header('Content-Disposition', 'attachment; filename=%s' % (os.path.basename(filename)))
			rootmsg.attach(a)
		
	
	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.

	
	# Send the message via local SMTP server.
	try:
		s = smtplib.SMTP('mint.nitric.co.za', 25)
		#s.login(settings.smtpuser, settings.smtppass)
	except AttributeError:
		s = smtplib.SMTP('localhost')
	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	s.sendmail(mailfrom, mailto, rootmsg.as_string())
	s.close()


def sendtext(mailto, mailfrom, subject, text):
	msg = MIMEText(text)
	msg['Subject'] = subject
	msg['From'] = mailfrom
	msg['To'] = mailto
	s = smtplib.SMTP("localhost")
	s.sendmail(mailfrom, [mailto], msg.as_string())
	s.close()
	


	
	
