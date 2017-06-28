# SUD-MQTT
Read Seneye USB Device and transmit readings via MQTT

# Requirements
- PyYAML
- PyUSB
- MQTT, I used Paho MQTT
- Seneye device (https://www.seneye.com)
- Linux single-board computer (Odroid, Raspberry Pi, ...)
- MQTT broker

# Usage
1. Copy config.yml.template to config.yml and edit selecting 
-- your device, 
-- MQTT broker, 
-- and publication topic
1. Run this Python program as a daemon, Google is your friend
