#!/usr/bin/python3

import socket, time, requests, datetime

oldfreq = '0'
oldmode = 'none'


key ='cl55424543511056' #Your cloudlog API key
radio_name = "FT-817"  #Your Radio Name
cloudurl = "http://www.youraddress.com/index.php/api/radio" #Radio API address
host = "127.0.0.1" #Rigctld IP address
port = 4532 #Rigctld port


s=socket.socket()
s.connect((host, port))

while True:
	s.send(b'f\n')
	newfreq = s.recv(1024).decode().strip()
	s.send(b'm\n')
	newmode = s.recv(1024).decode().strip().split()[0]
	if newfreq != oldfreq or newmode != oldmode:
		ts=datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M")
		payload = {'key':key,'radio':radio_name,'frequency':newfreq,'mode':newmode,'timestamp':ts}
		r = requests.post(cloudurl, json=payload)
		print("Response: "+str(r.status_code))
		oldfreq = newfreq
		oldmode = newmode
	time.sleep(1)
	
s.close()

