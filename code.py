import time
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
import adafruit_rfm9x
import config

def purple(data):
  stamp = time.time()
  return "\x1b[38;5;104m[" + str(stamp) + "] " + data + "\x1b[0m"

def yellow(data):
  return "\x1b[38;5;220m" + data + "\x1b[0m"

def red(data):
  return "\x1b[1;5;31m -- " + data + "\x1b[0m"

# our version
VERSION = "RF.Guru_2P_MagLoopSwitch_LoRa 0.1" 

rf1 = DigitalInOut(board.GP13)
rf1.direction = Direction.OUTPUT
rf1.value = False
time.sleep(0.01)

rf2 = DigitalInOut(board.GP14)
rf2.direction = Direction.OUTPUT
rf2.value = False
time.sleep(0.01)

ports = {
  "1": rf1,
  "2": rf2,
}

for number, port in ports.items():
    port.value = False
    time.sleep(0.01)

if config.default_port is not 0:
  ports[str(int(config.default_port))].value = True

print(red(config.name + " -=- " + VERSION))

# Lora Stuff
RADIO_FREQ_MHZ = 868.000
CS = DigitalInOut(board.GP21)
RESET = DigitalInOut(board.GP20)
spi = busio.SPI(board.GP10, MOSI=board.GP11, MISO=board.GP8)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ, baudrate=1000000, agc=False,crc=True)
rfm9x.tx_power = 5

while True:
    msg = yellow("Waiting for LoRa packet ...")
    print(f"{msg}\r", end="")
    packet = rfm9x.receive(with_header=True,timeout=10)

    if packet is not None:
        #print(packet)
        if packet[:3] == (b'<\xaa\x01'):
                rawdata = bytes(packet[3:]).decode('utf-8')
                if rawdata.startswith(config.name):
                    try:
                        if ports[str(int(rawdata[-1]))].value is True:
                          ports[str(int(rawdata[-1]))].value = False
                          print(purple("PORT REQ: Turned port " + str(int(rawdata[-1])) + " off"))
                        elif ports[str(int(rawdata[-1]))].value is False:
                          ports[str(int(rawdata[-1]))].value = True
                          print(purple("PORT REQ: Turned port " + str(int(rawdata[-1])) + " on"))
                    except:
                        print(purple("PORT REQ: Wrong Port NR"))
                else:
                    print(yellow("Received another switch port req packet: " + str(rawdata)))
        else:
            print(yellow("Received an unknown packet: " + str(packet)))