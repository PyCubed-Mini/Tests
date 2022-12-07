from radio_utils import headers


def receive(rfm9x, with_ack=True):
    """Recieve a packet.  Returns None if no packet was received.
    Otherwise returns (header, payload)"""
    packet = rfm9x.receive(with_ack=with_ack, with_header=True, debug=True)
    if packet is None:
        return None
    return packet[0:6], packet[6:]


def print_res(res):
    if res is None:
        print("No packet received")
    else:
        header, payload = res
        print("Received (raw header):", [hex(x) for x in header])
        if header[5] == headers.DEFAULT:
            print('Received beacon')
        else:
            packet_text = str(payload, "utf-8")
            print(packet_text)


class _data:

    def __init__(self):
        self.msg = bytes([])
        self.msg_last = bytes([])
        self.cmsg = bytes([])
        self.cmsg_last = bytes([])


def read_loop(rfm9x):
    data = _data()

    while True:
        res = receive(rfm9x)
        if res is None:
            continue
        header, payload = res

        oh = header[5]
        if oh == headers.DEFAULT:
            print(payload)
        elif oh == headers.NAIVE_START or oh == headers.NAIVE_MID or oh == headers.NAIVE_END:
            print('Recieved Naive')
            handle_naive(oh, data, payload)
        elif oh == headers.CHUNK_START or oh == headers.CHUNK_MID or oh == headers.CHUNK_END:
            print('Recieved chunk')
            handle_chunk(oh, data, payload)


def handle_naive(header, data, response):
    if header == headers.NAIVE_START:
        data.msg_last = response
        data.msg = response
    else:
        if response != data.msg_last:
            data.msg += response
        else:
            data.debug('Repeated chunk')

    if header == headers.NAIVE_END:
        data.cmsg_last = bytes([])
        data.msg = str(data.msg, 'utf-8')
        print(data.msg)


def handle_chunk(header, data, response):
    if header == headers.CHUNK_START:
        data.cmsg = response
        data.cmsg_last = response
    else:
        if response != data.cmsg_last:
            data.cmsg += response
        else:
            data.debug('Repeated chunk')
        data.cmsg_last = response

    if header == headers.CHUNK_END:
        data.ccmsg_last = bytes([])
        data.cmsg = str(data.cmsg, 'utf-8')
        print('Recieved message chunk')
        print(data.cmsg)
