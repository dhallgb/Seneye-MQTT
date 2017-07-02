#!/usr/bin/env python
#
# Read Seneye SUD and publish readings to MQTT
# MQTT is published using the 'single' publish instead of opening a client connection
# See the file protocol.mdown for a description of the SUD communications flow
#
import paho.mqtt.publish as publish
import usb.core, usb.util
import sys, json, pprint
from bitstring import BitArray
interface=0
hostname='lonna'
topic='raw/aquarium'
vendor=9463
product=8708

def printhex(s):
    return(type(s),len(s),":".join("{:02x}".format(c) for c in s))

def setup_up():
    # find the device using product id strings
    dev = usb.core.find(idVendor=vendor, idProduct=product)
    if __debug__:
        print("device       >>>",dev)
    return(dev)

def read_sud(dev, interface):
    # release kernel driver if active
    if dev.is_kernel_driver_active(interface):
        dev.detach_kernel_driver(interface)

    # by passing no parameter we pick up the first configuration, then claim interface, in that order
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

    # write to device with hello string
    msg="HELLOSUD"
    rc=dev.write(epOut,msg)
    if __debug__:
        print("HELO ret code>>>",rc)

    # read from device
    ret=dev.read(epIn,epIn.wMaxPacketSize)
    if __debug__:
        print("HELO hex     >>>",printhex(ret))

    # write to device with reading request
    msg="READING"
    rc=dev.write(epOut,msg)
    if __debug__:
        print("READ ret code>>>",rc)

    # read from device twice, first for return from "READING", second for actual values
    ret=dev.read(epIn,epIn.wMaxPacketSize,1000)
    ret=dev.read(epIn,epIn.wMaxPacketSize,10000)
    c = BitArray(ret)
    if __debug__:
        print("sensor hex   >>>",printhex(ret))
        print("sensor bits  >>>",c.bin)
        print("sensor bits len>",len(c.bin))

    # write to device with close string
    msg="BYESUD"
    rc=dev.write(epOut,msg)
    if __debug__:
        print("BYE ret code >>>",rc)
    return(c)

def mungReadings(p):
    # see protocol.mdown for explaination of where the bitstrings start and end
    s={}
    s['InWater']=p[33]
    s['SlideNotFitted']=p[34]
    s['SlideExpired']=p[35]
    ph=p[44:60]
    s['pH']=ph.int/100   # divided by 100
    nh3=p[60:72]
    s['NH3']=nh3.int/1000  # divided by 1000
    temp=p[72:104]
    s['Temp']=temp.int/1000 # divided by 1000
    if __debug__:
        pprint.pprint(s)
    j = json.dumps(s, ensure_ascii=False)
    return(j)

def clean_up(dev):
    # re-attach kernel driver
    usb.util.release_interface(dev, interface)
    dev.attach_kernel_driver(interface)
    # clean up
    usb.util.release_interface(dev, interface)
    usb.util.dispose_resources(dev)
    dev.reset()

def main():
    # open device
    device = setup_up()
    # read device
    sensor = read_sud(device, interface)
    # format into json
    readings=mungReadings(sensor)
    # push readings to MQTT broker
    publish.single(topic, readings, hostname=hostname)
    # close device
    clean_up(device)

if __name__ == "__main__":
    main()
