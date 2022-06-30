import board
import busio
import digitalio
import config
import binascii

import adafruit_rfm9x


# Define radio parameters.
RADIO_FREQ_MHZ = 433.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.D5)
RESET = digitalio.DigitalInOut(board.D6)
# Or uncomment and instead use these if using a Feather M0 RFM9x board and the appropriate
# CircuitPython build:
# CS = digitalio.DigitalInOut(board.RFM9X_CS)
# RESET = digitalio.DigitalInOut(board.RFM9X_RST)

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 23

# Send a packet.  Note you can only send a packet up to 252 bytes in length.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.
# rfm9x.send(bytes("Hello world!\r\n", "utf-8"))

while True:
    prompt = input('~>')
    if prompt == 'r':
        packet = rfm9x.receive(timeout=5.0)
        if packet is None:
            LED.value = False
            print("Received nothing!")
        else:
            LED.value = True
            print(f"Received (raw bytes): {packet}")
            packet_text = str(packet, "ascii")
            print(f"Received (ASCII): {packet_text}")
            rssi = rfm9x.last_rssi
            print(f"Received signal strength: {rssi} dB")
    elif prompt == 'rl': # Recieve on a loop
        print('Listening for packets...')
        while True:
            packet = rfm9x.receive()
            if packet is not None:
                LED.value = True
                print(f'Received (raw bytes): {packet}')
                packet_text = str(packet, "ascii")
                print(f"Received (ASCII): {packet_text}")
                rssi = rfm9x.last_rssi
                print(f"Received signal strength: {rssi} dB")
    elif len(prompt) == 1 and prompt[0] == 't':
        what = input('message=')
        rfm9x.send(bytes(what, "utf-8"))
    elif len(prompt) >= 2 and prompt[0:2] == 'ts':  # Transmit with secret code
        what = input('message=')
        rfm9x.send(config.secret_code+bytes(what, "utf-8"))
    elif len(prompt) >= 2 and prompt[0:2] == 'tc':  # Transmit command
        firstbyte = binascii.unhexlify(input("first byte="))
        secondbyte = binascii.unhexlify(input("second byte="))
        arguments = input('arguments=')
        msg = config.secret_code+firstbyte+secondbyte+bytes(arguments, "utf-8")
        print(f'sending {msg}')
        rfm9x.send(msg)
