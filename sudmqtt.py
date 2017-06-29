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

    endpoint = dev[0][(0,0)][0]
    data = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, timeout=1000)
    try:
        data = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, timeout=10)
    #    if data is not None and len(data) > 2:
        print(data)
    except usb.core.USBError as e:
        if e.errno != 110: # 110 is a timeout.
            sys.exit("Error readin data: %s" % str(e))

    # write to device with signature string
#    msg="HELLOSUD"
#    rc=dev.write(0x81,msg)
#    print("return code: ",rc)

    # re-attach kernel driver if it was active
    if kernel_driver_active:
        print("releasing interface")
        usb.util.release_interface(dev, interface)
        print("reattching kernel driver")
        dev.attach_kernel_driver(interface)

    usb.util.dispose_resources(dev)
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
