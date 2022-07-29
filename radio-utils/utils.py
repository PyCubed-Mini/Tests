def receive(rfm9x, with_ack=True):
    """Recieve a packet.  Returns None if no packet was received.
    Otherwise returns (header, payload)"""
    packet = rfm9x.receive(with_ack=with_ack, with_header=True)
    if packet is None:
        return None
    return packet[0:5], packet[5:]

def print_res(res):
    if res is None:
        print("No packet received")
    else:
        header, payload = res
        print("Received (raw header):", [hex(x) for x in header])
        packet_text = str(payload, "ascii")
        print(f"length: {packet_text}")