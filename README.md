# SUD-MQTT
Read Seneye USB Device and transmit readings via MQTT.
This project is an attempt to do some basic stuff: read from a Seneye device and transmit this information periodically to a MQTT endpoint, either local or remote, from where it can be integrated into whatever web dashboard you may choose.

# Requirements
- Python modules installed on base system
	- PyYAML installed using PIP 'pip install pyyaml'
	- PyUSB installed using PIP 'pip install pyusb'
	- MQTT, I used Paho MQTT installed using 'pip install paho-mqtt'
- Seneye device (https://www.seneye.com)
- Linux single-board computer (Odroid, Raspberry Pi, ...). I used a RaspPi Zero W which looks like a stick of gum...!
- MQTT broker such as Bluemix, HiveMQ, CloudMQTT, or see [here]: https://github.com/mqtt/mqtt.github.io/wiki/public_brokers
- if you need a dashboard, FreeBoard.io, Crouton (http://crouton.mybluemix.net/crouton/gettingStarted) are a couple

# Usage
1. copy config.yaml.template to config.yaml and edit changing at least
	- MQTT broker endpoint
	- publication topic
1. run periodically, I used cron
1. subscribe to the published topic