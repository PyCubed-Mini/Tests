import board
import busio
import digitalio
import config
from utils import read_loop
from lib.command_map import commands
from radio_utils.chunk import ChunkMessage
from radio_utils import headers

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

# set node/destination
rfm9x.node = 0xBA
rfm9x.destination = 0xAB

while True:
    prompt = input('~>')
    if prompt == 'rl' or prompt == 'read_loop':  # Recieve on a loop
        read_loop(rfm9x)
    elif prompt == 'uf' or prompt == 'upload_file':
        path = input('path=')
        msg = ChunkMessage(0, path)
        while True:
            packet, with_ack = msg.packet()

            debug_packet = str(packet)[:20] + "...." if len(packet) > 23 else packet
            print(f"Sending packet: {debug_packet}, with_ack: {with_ack}")

            if with_ack:
                if rfm9x.send_with_ack(packet):
                    msg.ack()
                else:
                   msg.no_ack()
            else:
                rfm9x.send(packet, keep_listening=True)

            if msg.done():
                break
    elif prompt == 'c' or prompt == 'command':  # Transmit particular command
        print(commands.keys())
        comand_bytes, will_respond = commands[input('command=')]
        args = input('arguments=')
        msg = bytes([headers.COMMAND]) + config.secret_code + comand_bytes + bytes(args, 'utf-8')
        while not rfm9x.send_with_ack(msg):
            print('Failed to send command')
            pass
        print('Successfully sent command')
        if will_respond:
            read_loop(rfm9x)
    elif prompt == 'h' or prompt == 'help':
        print('rl: read_loop')
        print('uf: upload_file')
        print('c: command')
        print('h: help')