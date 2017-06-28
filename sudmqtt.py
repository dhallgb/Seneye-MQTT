#!/usr/bin/env python
#
# Read Seneye SUD and publish readings to MQTT
# MQTT is published using the 'single' publish instead of opening a client connection
#
import paho.mqtt.publish as publish
import usb.core
import usb.util
import time
import yaml

# do some prelim work such as finding the seneye device
def setup():
    global config
    config = yaml.safe_load(open("config.yaml"))
    device = usb.core.find(idVendor=9463, idProduct=8708)          # should this be '0x...'?
    return(device)

# read the USB device using the handle passed from the usb.core.find
def readSUD(dev):
    interface = 0
    kernel_driver_active = False
    # release kernel driver if active
    if dev.is_kernel_driver_active(interface) is True:
        kernel_driver_active = True 
        print("releasing kernel driver")
        dev.detach_kernel_driver(interface)

    # set configuration picking up the first one (no parameter), and claim interface
    dev.set_configuration()
    usb.util.claim_interface(dev, interface)
    cfg = dev.get_active_configuration()
    print("configuration>>>",cfg)
    intf = cfg[(0,0)]
    print("interface>>>",intf)

# The SUD device seems to have these 2 types of transfers: interrupt and bulk.
# These are the endpoints: (got by printing the configuration above)
#   ENDPOINT 0x81: Interrupt IN
#   ENDPOINT 0x1: Interrupt OUT
#   ENDPOINT 0x82: Bulk IN
#   ENDPOINT 0x2: Bulk OUT



#    dev.write(1,"HELLOSUD")

    # re-attach kernel driver if it was active
    if kernel_driver_active:
        print("releasing interface")
        usb.util.release_interface(dev, interface)
        print("reattching kernel driver")
        dev.attach_kernel_driver(interface)

    return('sud readings')

# loop over reading from SUD, publishing to MQTT broker, and resting for timeout
def main():
    dev = setup()
    while True:
        readings = readSUD(dev)
        publish.single(config['mqtt']['topic'], readings, hostname=config['mqtt']['url'])
        time.sleep(config['sud']['loop'])

if __name__ == "__main__":
    main()
