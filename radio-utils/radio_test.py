import radio_headers as headers
import config as config
from lib.naive import NaiveMessage
import struct


states = ["Normal", "Safe", "DeTumble"]
states.sort()

def print_beacon(packet):
    unpacked = struct.unpack('b'+'f'*11, packet[5:])
    gyro = unpacked[3:6]
    acc = unpacked[6:9]
    mag = unpacked[9:12]
    print(f"State:        {states[unpacked[0]]}")
    print(f"CPU temp:     {unpacked[1]}")
    print(f"IMU Temp:     {unpacked[2]}")
    print(f"Gyro:         {gyro}")
    print(f"Acceleration: {acc}")
    print(f"Magnetometer: {mag}")

def radio_test(rfm9x, LED):
    msg = ''
    last = None
    while True:
        packet = rfm9x.receive(with_ack=True, with_header=True)
        if packet is not None:
            LED.value = True
            header = packet[4]

            print("Received (raw header):", [hex(x) for x in packet[0:5]])

            if header == headers.DEFAULT:
                print_beacon(packet)
                # print("unpacked: ", struct.unpack('b'+'f'*11, packet[5:]))
                continue

            chunk = str(packet[5:], "ascii")
            if header == headers.NAIVE_START:
                msg = chunk
                last = chunk
                print("Starting receiving large message...\n")
            elif header == headers.NAIVE_MID:
                if last == chunk:
                    print('Duplicate packet')
                else:
                    msg += chunk
            if header == headers.NAIVE_END:
                msg += chunk
                break

    print('msg: ', msg)

    if msg == config.test_message:
        print("Sucessfully received large message!\n")
    else:
        print("Failed to receive large message!\n")
    assert(msg == config.test_message)

    # Now transmit the large message back
    msg = NaiveMessage(0, msg)
    while not msg.done():
        packet, with_ack = msg.packet()
        debug_packet = str(packet)[:20] + \
            "...." if len(packet) > 23 else packet
        print(f"Sending packet: {debug_packet}")

        if with_ack:
            if rfm9x.send_with_ack(packet):
                msg.ack()
            else:
                msg.no_ack()
        else:
            rfm9x.send(packet, keep_listening=True)

    print("Message successfully sent!")
