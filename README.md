# Read Seneye via MQTT
This project is an attempt to do some basic stuff: read from a Seneye USB device ('SUD') and transmit this information periodically to a MQTT endpoint.

## Requirements
- Python libraries pprint, pyusb, mqtt (installed using 'pip install paho-mqtt')
- Seneye device (https://www.seneye.com)
- microUSB adapter if your SBC does not have a normal size USB connection
- Linux SBC ('single-board computer' - Odroid, Raspberry Pi, ...)
- MQTT broker such as Bluemix, HiveMQ, CloudMQTT, or see https://github.com/mqtt/mqtt.github.io/wiki/public_brokers
- If you need a dashboard, FreeBoard.io, Crouton (http://crouton.mybluemix.net/crouton/gettingStarted) are a couple

## Usage
1. Activate your SUD via Seneye Connect on a Windows machine, and insert a slide 
1. Install prerequisites as above on your SBC
1. Connect your Seneye SUD to your SBC
1. Access the USB without using sudo, perhaps by:
	- installing the 10-local.rules file into your /etc/udev/rules.d/ directory
	- add the user who will run this program to the 'plugdev' group ('sudo usermod -a -G plugdev userid')
	- activate the new udev rule ('sudo udevadm trigger')
1. Run periodically, for example using cron
1. Use MQTT to subscribe to the published topic elsewhere and put it on a dashboard