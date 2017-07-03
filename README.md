# Read Seneye via MQTT
This program reads from a Seneye USB device ('SUD') and transmits this information to an MQTT broker.

***Warning***
We are utilising the SUD outside its design boundaries, thanks to the kindness of Seneye in releasing the C++ code. Please be aware that you may damage your device by tinkering with it like this.

## Requirements
- Seneye USB device
- Python libraries pprint, pyusb, paho-mqtt 
- Linux SBC ('single-board computer' - Odroid, Raspberry Pi, ...)
- microUSB adapter if your SBC does not have a normal size USB connection
- MQTT broker such as Bluemix, HiveMQ, CloudMQTT, or see https://github.com/mqtt/mqtt.github.io/wiki/public_brokers
- If you need a dashboard, FreeBoard.io, Crouton (http://crouton.mybluemix.net/crouton/gettingStarted) are a couple

## Usage
1. Activate your SUD via Seneye Connect on a Windows machine, and insert a slide 
1. Install prerequisites as above on your SBC
1. Connect your Seneye SUD to your SBC
1. Gain access to the USB without using sudo, perhaps by:
	- installing the example 10-local.rules file into your /etc/udev/rules.d/ directory
	- add the user who will run this program to the __plugdev__ group `sudo usermod -a -G plugdev userid`
	- activate the new udev rule `sudo udevadm trigger`
1. Run periodically, for example using cron
1. To switch off debugging message use the optimize switch `python -O sudmqtt.py`
1. Use MQTT to subscribe to the published topic elsewhere and put it on a dashboard