#!/usr/bin/env python
#
# Read Seneye SUD and publish readings to MQTT
# MQTT is published using the 'single' publish instead of opening a client connection
# See the file protocol.mdown for a description of the SUD communications flow
#
import paho.mqtt.publish as publish
import usb.core, usb.util
import yaml, sys, json, pprint
from bitstring import BitArray
config=[]
device=[]
interface=0

def printhex(s):
    return(type(s),len(s),":".join("{:02x}".format(c) for c in s))

def setup_up():
    # find the device using product id strings
    dev = usb.core.find(idVendor=9463, idProduct=8708)
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
    # I start by assuming that short = 16 bits, int = 32 bits
    #
    #int Ts;
    #bit reserved : 2;
    #bit InWater : 1;
    #bit SlideNotFitted : 1;
    #bit SlideExpired : 1;
    #bit StateT : 2;
    #bit StatePh : 2;
    #bit StateNh3 : 2;
    #bit Error : 1;
    #bit IsKelvin : 1;
    #char reserved[8];   this is 64 bits long!
    #int  Kelvin;
    #int  x;
    #int  y;
    #int  Par;
    #int  Lux;
    #char  PUR;
    #short pH;
    #short Nh3;
    #int  T; - I presume that this is temperature
    #char reserved[16];
    s={}
    i=36 # this is the start of the data, so int + 2 bits = 34, right??!!?!?!
    s['InWater']=p[i]
    s['SlideNotFitted']=p[i+1]
    s['SlideExpired']=p[i+2]
    s['StateT']=p[i+3:i+4]
    s['StatePh']=p[i+5:i+6]
    s['StateNh3']=p[i+7:i+8]
    s['Error']=p[i+9]
    s['IsKelvin']=p[i+10]
    s['Temp']=p[i+7:i+8]
    s['pH']=p[i+7:i+8]
    s['NH3']=p[i+7:i+8]

    if __debug__:
        pprint.pprint(s)
    return(None)

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
    # open device
    device = setup_up()
    # read device
    sensor = read_sud(device, interface)
    # format into json
    readings=mungReadings(sensor)
    # push readings to MQTT broker
    publish.single(config['mqtt']['topic'], readings, hostname=config['mqtt']['url'])
    # close device
    clean_up(device)

if __name__ == "__main__":
    main()
