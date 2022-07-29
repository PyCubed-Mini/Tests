import radio_headers as headers
import config as config

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
            print(f"Received (raw payload): {chunk}")
            print(f"length: {len(packet)}")
            print(f"Received RSSI: {rfm9x.last_rssi}")

            if header == headers.NAIVE_START:
                msg = ''
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