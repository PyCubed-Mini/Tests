import board
import busio
import digitalio

import adafruit_rfm9x
from msgpack import pack

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

fails = 0
passes = 0


RADIO_FREQ_MHZ = 433.0  # Frequency of the radio in Mhz. Must match your

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.D5)
RESET = digitalio.DigitalInOut(board.D6)
# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
# word, encryption, frequency deviation, or other settings!
# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 13

# Send a packet.  Note you can only send a packet up to 252 bytes in length.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.
# rfm9x.send(bytes("Test Message 1\n", "utf-8"))

# Wait to receive packets.  Note that this library can't receive data at a fast
# rate, in fact it can only receive and process one 252 byte packet at a time.
# This means you should only use this for low bandwidth scenarios, like sending
# and receiving a single message at a time.
print("Awaiting Beacon (25s)")
beacon = False
beacon_text = "Hello World!"
for i in range(5):
    packet = rfm9x.receive(timeout=5.0)

    if packet is None:
        print("[Attempt {0}]: no message was received".format(i+1))
    else:
        #  print("Received (raw bytes): {0}".format(packet))
        packet_text = str(packet, "ascii")
        if packet_text == beacon_text:
            print(OKGREEN+"[Pass]: "+ENDC+"beacon task sucessful")
            passes += 1
            beacon = True
            break
        else:
            print("[Attempt {0}]: wrong message received".format(i+1))
            print("received {0} expected {1}".format(packet_text, beacon_text))
        rssi = rfm9x.last_rssi
        # print("Received signal strength: {0} dB".format(rssi))
if not beacon:
    fails+=1
    print(WARNING+"[Fail]: "+ENDC +" 'Hello World!' beacon was not received")



print("Tests Complete. {0}/{1} tests passed.".format(passes, passes+fails))


while True:
    pass
