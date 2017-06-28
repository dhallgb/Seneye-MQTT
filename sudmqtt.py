#!/usr/bin/env python
#
# Read Seneye SUD and publish readings to MQTT
#
import paho.mqtt.publish as publish
import usb.core
import yaml
loop=60  # read loop in seconds

# read config, file string can contain a path if needed

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# do some prelim work such as finding the seneye device
# TBD: multiple devices?
def setup():
    config = yaml.safe_load(open("config.yaml"))
    print(config)
    device = usb.core.find(idVendor=9463, idProduct=8708)          # should this be '0x...'?
    return(device)

def readSUD(device):
    pass

def main():
    dev = setup()
    print(dev)
    while True:
        readings = readSUD(dev)
        publish.single("raw/aquarium", "readings", hostname="lonna")
        time.sleep(loop)

if __name__ == "__main__":
    main()
