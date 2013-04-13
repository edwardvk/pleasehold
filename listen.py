# This listen for data on a port, and plays it through as audio
import socket
import pyaudio
import time

HOST = ''                 
PORT = 9999 # Listen port

chunk =  1024

p = pyaudio.PyAudio()

channels = 1



while(1):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((HOST, PORT))
	sock.listen(1)
	conn, addr = sock.accept()
	print 'Connected by', addr
	stream = p.open(format = pyaudio.paFloat32,channels = 1,rate = 44100,output = True)
	while 1:
		data = conn.recv(chunk)
		stream.write(data)	
		if not data: break

	conn.close()
	stream.close()
	p.terminate()

	time.sleep(2)
