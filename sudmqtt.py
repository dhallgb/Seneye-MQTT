#!/usr/bin/env python
#
# Read Seneye SUD and publish readings to MQTT
#
from weathericons import interpret_icons
import ujson
import machine
import time
Tx='G12'
server='lonna'
service='weatherunderground'
uartnum=1
pycom.heartbeat(False)

def setup():
    gc.enable()
    eink_init()
    eink_clear()
    eink_draw_line(300,0,300,599)
    eink_draw_line(300,200,799,200)
    eink_draw_line(300,400,799,400)
    eink_update()

def weather_msg(topic, msg):
    pycom.rgbled(0x007f00)
    time.sleep(1)
    pycom.rgbled(0x000000)
    weather=ujson.loads(msg)
    icon=interpret_icons(service,weather["iconid"])
    eink_set_en_font(ASCII32)
    eink_disp_string(icon["label"], 50, 250)
    eink_disp_bitmap(icon["icon"]+'.BMP', 100, 100)
    eink_set_en_font(ASCII64)
    eink_disp_string(str(weather["temperature"]), 100, 350)
    for i in range(1,4):
        y = ((i*2)-1)*100
        eink_disp_string(str(weather["forecast"][i]["low"]),400,y)
        eink_disp_string(str(weather["forecast"][i]["high"]),600,y)
    eink_update()

def main1():
    setup()
    c = MQTTClient("eink_display", server)
    c.set_callback(weather_msg)
    c.connect()
    c.subscribe(b"raw/weather")
    while True:
        if True:
            print("one>>",gc.mem_free())
            c.wait_msg()
        else:
            print("two>>",gc.mem_free())
            c.check_msg()
            time.sleep(55)
    c.disconnect()

def main2():
    setup()
    c = MQTTClient("eink_display", server)
    c.set_callback(weather_msg)
    c.subscribe(b"raw/weather")
    while True:
        c.connect()
        c.check_msg()
        c.disconnect()
        time.sleep(55)
        print("two>>",gc.mem_free())

if __name__ == "__main__":
    main()

