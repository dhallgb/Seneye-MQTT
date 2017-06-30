#!/usr/bin/env python
#
# Read Seneye SUD and publish readings to MQTT
# MQTT is published using the 'single' publish instead of opening a client connection
# See the file protocol.mdown for a description of the SUD communications flow
#
import paho.mqtt.publish as publish
import usb.core
import usb.util
import yaml
import sys
import atexit
config=[]
device=[]
interface=0

def read_sud(dev, interface):
    # release kernel driver if active
    if dev.is_kernel_driver_active(interface):
        dev.detach_kernel_driver(interface)

    # by passing no parameter we pick up the first configuration, then claim interface
    dev.set_configuration()
    usb.util.claim_interface(dev, interface)
    configuration = dev.get_active_configuration()
    interface = configuration[(0,0)]

    if __debug__:
        print("configuration>>>",configuration)
        print("interface    >>>",interface)

    # find the first in and out endpoints in our interface
    epIn = usb.util.find_descriptor(interface, custom_match= lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
    epOut = usb.util.find_descriptor(interface, custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)

    # were our endpoints found?
    assert epIn is not None
    assert epOut is not None
    if __debug__:
        print("endpoint in  >>>",epIn)
        print("endpoint out >>>",epOut)

    # write to device with signature string
    msg="HELLOSUD"
    rc=dev.write(epOut,msg)
    if __debug__:
        print("HELO ret code>>>",rc)

    # read from device
    ret=dev.read(epIn,epIn.wMaxPacketSize)
    sret = ''.join([chr(x) for x in ret])
    if __debug__:
        print("return       >>>",ret)
        print("return string>>>",sret)

    # write to device with reading request
    msg="READING"
    rc=dev.write(epOut,msg)
    if __debug__:
        print("READ ret code>>>",rc)

    # read from device
    ret=dev.read(epIn,epIn.wMaxPacketSize,1000)
    sret = ''.join([chr(x) for x in ret])
    if __debug__:
        print("return       >>>",ret)
        print("return string>>>",sret)

    # read from device again
    ret=dev.read(epIn,epIn.wMaxPacketSize,1000)
    sret = ''.join([chr(x) for x in ret])
    if __debug__:
        print("return       >>>",ret)
        print("return string>>>",sret)

    # write to device with close string
    msg="BYESUD"
    rc=dev.write(epOut,msg)
    if __debug__:
        print("BYE ret code >>>",rc)
    return(sret)

def clean_up(dev):
    # re-attach kernel driver
    usb.util.release_interface(dev, interface)
    dev.attach_kernel_driver(interface)
    # clean up
    usb.util.release_interface(dev, interface)
    usb.util.dispose_resources(dev)
    dev.reset()

def main():
    # load config
    config = yaml.safe_load(open("config.yaml"))
    # find the device using product id strings
    device = usb.core.find(idVendor=9463, idProduct=8708)
    if __debug__:
        print("device       >>>",device)
    sensor=read_sud(device, interface)
    # push readings to MQTT broker
    publish.single(config['mqtt']['topic'], sensor, hostname=config['mqtt']['url'])
    clean_up(device)

if __name__ == "__main__":
    main()
