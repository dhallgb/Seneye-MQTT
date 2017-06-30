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

def main():
    # load config
    config = yaml.safe_load(open("config.yaml"))

    # find the device using product id strings
    dev = usb.core.find(idVendor=9463, idProduct=8708)
    print("device       >>>",dev)

    # release kernel driver if active
    interface = 0
    was_kernel_driver_active = False
    if dev.is_kernel_driver_active(interface) is True:
        was_kernel_driver_active = True 
        dev.detach_kernel_driver(interface)

    # by passing no parameter we pick up the first configuration, then claim interface
    dev.set_configuration()
    usb.util.claim_interface(dev, interface)
    configuration = dev.get_active_configuration()
    print("configuration>>>",configuration)
    interface = configuration[(0,0)]
    print("interface    >>>",interface)

    # find the first in and out endpoints in our interface
    epIn = usb.util.find_descriptor(interface, custom_match= lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
    epOut = usb.util.find_descriptor(interface, custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)

    # were our endpoints found?
    assert epIn is not None
    assert epOut is not None

    print("endpoint in  >>>",epIn)
    print("endpoint out >>>",epOut)

#
#    interface_number = cfg[(0,0)].bInterfaceNumber
#    alternate_setting = usb.control.get_interface(dev,interface_number)
#    intf = usb.util.find_descriptor(
#            cfg, bInterfaceNumber = interface_number,
#            bAlternateSetting = alternate_setting
#        )
#

    # write to device with signature string
    msg="HELLOSUD"
    rc=dev.write(epOut,msg)
    print("return code  >>>",rc)

    # read from device
    ret=dev.read(epIn,epIn.wMaxPacketSize)
    sret = ''.join([chr(x) for x in ret])
    print("return       >>>",ret)
    print("return string>>>",sret)

    # re-attach kernel driver if it was active
    if was_kernel_driver_active:
        print("releasing interface")
        usb.util.release_interface(dev, interface)
        print("reattaching kernel driver")
#        dev.attach_kernel_driver(interface)

    usb.util.release_interface(dev, interface)
    usb.util.dispose_resources(dev)
    dev.reset()

    # push readings to MQTT broker
    publish.single(config['mqtt']['topic'], sret, hostname=config['mqtt']['url'])

if __name__ == "__main__":
    main()
