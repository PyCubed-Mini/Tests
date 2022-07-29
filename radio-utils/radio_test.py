import radio_headers as headers
import config as config
from lib.naive import NaiveMessage

def radio_test(rfm9x, LED):
    msg = ''
    last = None
    while True:
        packet = rfm9x.receive(with_ack=True, with_header=True)
        if packet is not None:
            LED.value = True
            header = packet[4]
            chunk = str(packet[5:], "ascii")

            print("Received (raw header):", [hex(x) for x in packet[0:5]])
            # print(f"Received (raw payload): {chunk}")
            # print(f"length: {len(packet)}")
            # print(f"Received RSSI: {rfm9x.last_rssi}")

            if header == headers.NAIVE_START:
                msg = chunk
                last = chunk
                print("Starting receiving large message...")
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
        print("Sucessfully received large message!")
    else:
        print("Failed to receive large message!")
    assert(msg == config.test_message)

    # Now transmit the large message back
    msg = NaiveMessage(0, msg)
    while not msg.done():
        packet, with_ack = msg.packet()
        debug_packet = str(packet)[:20] + "...." if len(packet) > 23 else packet
        print(f"Sending packet: {debug_packet}")

        if with_ack:
            if rfm9x.send_with_ack(packet):
                msg.ack()
            else:
                msg.no_ack()
        else:
            rfm9x.send(packet, keep_listening=True)

    print("Message successfully sent!")
