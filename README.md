Python client to query rigctrld and report radio frequency/mode to CloudLog

Modify these top lines:

	key ='cl55424543511056' #Your cloudlog API key
	radio_name = "FT-817"  #Your Radio Name
	cloudurl = "http://www.youraddress.com/index.php/api/radio" #Radio API address
	host = "127.0.0.1" #Rigctld IP address
	port = 4532 #Rigctld port

Then be sure to select your radio under the station tab while on the QSO screen for the updated band/mode data to show.
