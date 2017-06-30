#!/usr/bin/env python
#
# Read Seneye SUD and publish readings to MQTT
# MQTT is published using the 'single' publish instead of opening a client connection
# See the file protocol.mdown for a description of the SUD communications flow
#
import paho.mqtt.publish as publish
import usb.core
import usb.util
import time
import yaml
import sys

def readSUD():
    # find the device using product id strings
    dev = usb.core.find(idVendor=9463, idProduct=8708)
    print("device>>>",dev)

    # release kernel driver if active
    interface = 0
    was_kernel_driver_active = False
    if dev.is_kernel_driver_active(interface) is True:
        was_kernel_driver_active = True 
        dev.detach_kernel_driver(interface)

    # by passing no parameter we pick up the first configuration, and claim interface
    dev.set_configuration()
    usb.util.claim_interface(dev, interface)
    cfg = dev.get_active_configuration()
    print("configuration>>>",cfg)
    intf = cfg[(0,0)]
    print("interface>>>",intf)

    # set the base endpoint, and attempt a read
    endpoint = dev[0][(0,0)][0]
    try:
        data = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, timeout=1000)
        if data is not None and len(data) > 2:
            print(data)
    except usb.core.USBError as e:
        sys.exit("Error reading data: %s" % str(e))

    # write to device with signature string
#    msg="HELLOSUD"
#    rc=dev.write(0x81,msg)
#    print("return code: ",rc)

    # re-attach kernel driver if it was active
    if was_kernel_driver_active:
        print("releasing interface")
        usb.util.release_interface(dev, interface)
        print("reattching kernel driver")
        dev.attach_kernel_driver(interface)

    usb.util.dispose_resources(dev)
    return('readings')

def main():
    # main: load config, read device, publish readings
    config = yaml.safe_load(open("config.yaml"))
    readings = readSUD()
    publish.single(config['mqtt']['topic'], readings, hostname=config['mqtt']['url'])

if __name__ == "__main__":
    main()
