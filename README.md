# SUD-MQTT
Read Seneye USB Device and transmit readings via MQTT.
This project is an attempt to do some basic stuff: read from a Seneye device and transmit this information periodically to a MQTT endpoint, either local or remote, from where it can be integrated into whatever web dashboard you may choose.

# Requirements
- Python modules installed on base system
	- PyYAML installed using PIP 'pip install pyyaml'
	- PyUSB installed using PIP 'pip install pyusb'
	- MQTT, I used Paho MQTT installed using 'pip install paho-mqtt'
- Seneye device (https://www.seneye.com)
- Linux single-board computer (Odroid, Raspberry Pi, ...). I used a RasPi Zero W which looks like a stick of gum...!
- MQTT broker such as Bluemix, HiveMQ, CloudMQTT, or see https://github.com/mqtt/mqtt.github.io/wiki/public_brokers
- if you need a dashboard, FreeBoard.io, Crouton (http://crouton.mybluemix.net/crouton/gettingStarted) are a couple
- normally USB devices cannot be accessed without root authority, so if you want to run without using the sudo command, try putting something like the 10-local.rules file into your /etc/udev/rules.d/ directory (and change group to a group to which you belong - use 'groups' command to find out which). To understand this better search the internet for "access USB without sudo"

# Usage
1. Using a microusb adapter connect your Seneye SUD to the microusb port of a RasPi Zero
1. Install prerequisites as above
1. copy config.yaml.template to config.yaml and edit changing at least
	- MQTT broker endpoint
	- publication topic
1. run periodically, I used cron
1. subscribe to the published topic and put it on a dashboard