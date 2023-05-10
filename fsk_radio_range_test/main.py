# Simple circuitpython receiver to verify radio hardware
import board
import busio
import digitalio
import lib.adafruit_rfm9x_fsk as adafruit_rfm9x
import time


# print formatters
bold = '\033[1m'
normal = '\033[0m'
red = '\033[31m'
green = '\033[32m'
yellow = '\033[33m'
blue = '\033[34m'

# test messages - must be less than 59 bytes
msg_1 = f"{bold}{yellow}111:{normal} Outer space exists beyond Earth."
msg_2 = f"{bold}{green}222:{normal} A planet is an astronomical body."
msg_3 = f"{bold}{yellow}333:{normal} A planet is large and rounded."
msg_4 = f"{bold}{green}444:{normal} Planets are not stars."
msg_5 = f"{bold}{yellow}555:{normal} But, planets form around stars."
msg_6 = f"{bold}{green}666:{normal} Planets form in protoplanetary disks."


messages = [msg_1, msg_2, msg_3, msg_4, msg_5, msg_6]


def get_input_discrete(prompt_str, choice_values):
    print(prompt_str)
    choice = None

    choice_values_str = "("
    for i, _ in enumerate(choice_values):
        choice_values_str += f"{choice_values[i]}"
        if i < len(choice_values) - 1:
            choice_values_str += ", "
    choice_values_str += ")"

    choice_values = [cv.lower() for cv in choice_values]

    while choice not in choice_values:
        choice = input(f"{choice_values_str} ~> ").lower()
    return choice


def set_param_from_input_discrete(param, prompt_str, choice_values, allow_default=False, type=int):

    # add "enter" as a choice
    choice_values = [""] + choice_values if allow_default else choice_values
    prompt_str = prompt_str + \
        " (enter to skip):" if allow_default else prompt_str

    choice = get_input_discrete(prompt_str, choice_values)

    if choice == "":
        return param
    else:
        return type(choice)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_input_range(prompt_str, choice_range):
    print(prompt_str)
    choice = None

    choice_range_str = f"({choice_range[0]} - {choice_range[1]})"

    while True:
        choice = input(f"{choice_range_str} ~> ").lower()
        if choice == "":
            break

        if not is_number(choice):
            continue

        if float(choice) >= choice_range[0] and float(choice) <= choice_range[1]:
            break
    return choice


def set_param_from_input_range(param, prompt_str, choice_range, allow_default=False):

    # add "enter" as a choice
    prompt_str = prompt_str + \
        " (enter to skip):" if allow_default else prompt_str

    choice = get_input_range(prompt_str, choice_range)

    if choice == "":
        return param
    else:
        return float(choice)


print(f"\n{bold}{yellow}Radio Range Test{normal}\n")

board_str = get_input_discrete(
    f"""Select the board/radio:
        {bold}(s){normal} satellite,
        {bold}(f){normal} feather,
        {bold}(p){normal} raspberry pi,
        {bold}(t){normal} RPiGS TX,
        {bold}(r){normal} RPiGS RX,
        """,
    ["s", "f", "p", "t", "r"]
)


def satellite_spi_config():
    # pocketqube
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

    cs = digitalio.DigitalInOut(board.RF_CS)
    reset = digitalio.DigitalInOut(board.RF_RST)
    cs.switch_to_output(value=True)
    reset.switch_to_output(value=True)

    return spi, cs, reset


def feather_spi_config():
    # feather
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

    cs = digitalio.DigitalInOut(board.D5)
    reset = digitalio.DigitalInOut(board.D6)
    cs.switch_to_output(value=True)
    reset.switch_to_output(value=True)

    return spi, cs, reset


def pi_spi_config():
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

    cs = digitalio.DigitalInOut(board.ce1)
    reset = digitalio.DigitalInOut(board.d25)

    return spi, cs, reset


def rpigs_tx_spi_config():
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

    cs = digitalio.DigitalInOut(board.D7)
    reset = digitalio.DigitalInOut(board.D25)

    return spi, cs, reset


def rpigs_rx_spi_config():
    spi = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)

    cs = digitalio.DigitalInOut(board.D16)
    reset = digitalio.DigitalInOut(board.D24)

    return spi, cs, reset


if board_str == "s":
    spi, cs, reset = satellite_spi_config()
    print(f"{bold}{green}Satellite{normal} selected")
elif board_str == "f":
    spi, cs, reset = feather_spi_config()
    print(f"{bold}{green}Feather{normal} selected")
elif board_str == "p":
    spi, cs, reset = pi_spi_config()
    print(f"{bold}{green}Raspberry Pi{normal} selected")
elif board_str == "t":
    spi, cs, reset = rpigs_tx_spi_config()
    print(f"{bold}{green}Raspberry Pi{normal} selected")
elif board_str == "r":
    spi, cs, reset = rpigs_rx_spi_config()
    print(f"{bold}{green}Raspberry Pi{normal} selected")
else:
    raise ValueError(f"Board string {board_str} invalid")

# Initialze RFM radio
RADIO_FREQ_MHZ = 433.0
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, RADIO_FREQ_MHZ)

node_str = get_input_discrete(
    f"Node {bold}A{normal} or {bold}B{normal}",
    ["A", "B"]
)

if node_str == "a":
    rfm9x.node = 0xAA
    rfm9x.destination = 0xBB
else:
    rfm9x.destination = 0xAA
    rfm9x.node = 0xBB

# RFM radio configuration

param_str = get_input_discrete(
    f"Change radio parameters? {bold}(y/n){normal}", ["y", "n"])

# start by setting the defaults
rfm9x.frequency_mhz = 433.0
rfm9x.tx_power = 23
rfm9x.bitrate = 1200
rfm9x.frequency_deviation = 10000
rfm9x.rx_bandwidth = 25.0
timeout = 10
rfm9x.preamble_length = 16
rfm9x.ack_delay = 0.2
rfm9x.ack_wait = 5
rfm9x.checksum = True

if param_str == "y":
    rfm9x.frequency_mhz = set_param_from_input_range(rfm9x.frequency_mhz, f"Frequency (currently {rfm9x.frequency_mhz} MHz)",
                                                     [240.0, 960.0], allow_default=True)
    rfm9x.tx_power = set_param_from_input_discrete(rfm9x.tx_power, f"Power (currently {rfm9x.tx_power} dB)",
                                                   [f"{i}" for i in range(5, 24)], allow_default=True)
    rfm9x.bitrate = set_param_from_input_range(rfm9x.bitrate, f"Bitrate (currently {rfm9x.bitrate} bps)",
                                               [(adafruit_rfm9x._RH_RF95_FXOSC // 0xFFFF), 300000], allow_default=True)
    rfm9x.frequency_deviation = set_param_from_input_range(rfm9x.frequency_deviation, f"Frequency deviation (currently {rfm9x.frequency_deviation})",
                                                           [600, 200000], allow_default=True)
    rfm9x.rx_bandwidth = set_param_from_input_discrete(rfm9x.rx_bandwidth, f"Receiver filter bandwidth (single-sided, currently {rfm9x.rx_bandwidth})",
                                                       [f"{rfm9x._bw_bins_kHz[i]}" for i in range(len(rfm9x._bw_bins_kHz))], allow_default=True, type=float)
    rfm9x.lna_gain = set_param_from_input_discrete(rfm9x.lna_gain, f"LNA Gain - [max = 1, min = 6] (currently {rfm9x.lna_gain})",
                                                   [f"{i}" for i in range(1, 7)], allow_default=True)
    rfm9x.preamble_length = set_param_from_input_range(rfm9x.preamble_length, f"Preamble length (currently {rfm9x.preamble_length})",
                                                       [3, 2**16], allow_default=True)
    timeout = set_param_from_input_range(timeout, f"RX Timeout (currently {timeout} s)",
                                         [0.0, 1000.0], allow_default=True)
    rfm9x.ack_delay = set_param_from_input_range(rfm9x.ack_delay, f"Acknowledge delay (currently {rfm9x.ack_delay} s)",
                                                 [0.0, 10.0], allow_default=True)
    rfm9x.ack_wait = set_param_from_input_range(rfm9x.ack_wait, f"Acknowledge RX Timeout (currently {rfm9x.ack_wait} s)",
                                                [0.0, 100.0], allow_default=True)
    rfm9x.afc_enable = set_param_from_input_discrete(rfm9x.afc_enable, f"Enable automatic frequency calibration (AFC) (currently {rfm9x.afc_enable})",
                                                     ["0", "1"], allow_default=True)
    rfm9x.checksum = set_param_from_input_discrete(rfm9x.checksum, f"Enable checksum (currently {rfm9x.checksum})",
                                                   ["0", "1"], allow_default=True)

print(f"{yellow}{bold}Radio Parameters:{normal}")
print(f"\tNode addr = {rfm9x.node}\tDest addr = {rfm9x.destination}")
print(f"\tFrequency = {rfm9x.frequency_mhz} MHz")
print(f"\tPower = {rfm9x.tx_power} dBm")
print(f"\tBitrate = {rfm9x.bitrate} Hz")
print(f"\tFrequency Deviation = {rfm9x.frequency_deviation}")
print(f"\tRX filter bandwidth = {rfm9x.rx_bandwidth}")
print(f"\tLNA Gain [max = 1, min = 6] = {rfm9x.lna_gain}")
print(f"\tPreamble Length = {rfm9x.preamble_length}")
print(f"\tReceive timeout = {timeout} s")
print(f"\tAcknowledge delay = {rfm9x.ack_delay} s")
print(f"\tAcknowledge wait = {rfm9x.ack_wait} s")
print(f"\tAFC enabled = {rfm9x.afc_enable}")
print(f"\tChecksum enabled = {rfm9x.checksum}")

while True:

    mode_str = get_input_discrete(
        f"Operate in {bold}(r){normal}eceive or {bold}(t){normal}ransmit mode?",
        ["r", "t"])

    ack_str = get_input_discrete(
        f"Acknowledge? {bold}(y/n){normal}", ["y", "n"])

    ack = (ack_str == "y")

    if mode_str == "r":
        print(f"{bold}Receive{normal} mode selected, {'with acknowledge' if ack else 'no acknowledge'}")

        print(f"\n{yellow}Receiving (CTRL-C to exit)...{normal}")
        while True:
            try:
                msg = rfm9x.receive(with_ack=ack, debug=True, timeout=timeout)
                if msg is not None:
                    try:
                        print(f"(RSSI: {rfm9x.last_rssi} | FEI: {rfm9x.frequency_error}| AFC: {rfm9x.afc_value} | Freq: {rfm9x.frequency_mhz})\t" +
                              msg.decode("utf-8", "strict"))
                    except UnicodeError:
                        try:
                            # try to replace before totally giving up on decoding
                            print(f"(RSSI: {rfm9x.last_rssi} | FEI: {rfm9x.frequency_error}| AFC: {rfm9x.afc_value} | Freq: {rfm9x.frequency_mhz})\t{red}UnicodeError{normal}\t" +
                                  msg.decode("utf-8", "replace"))
                        except UnicodeError:
                            print(f"(RSSI: {rfm9x.last_rssi} | FEI: {rfm9x.frequency_error})\t{red}UnicodeError{normal}\t" +
                                  str(msg))

            except KeyboardInterrupt:
                break

    else:
        print(f"{bold}Transmit{normal} mode selected, {'with acknowledge' if ack else 'no acknowledge'}")

        while True:
            for i, msg in enumerate(messages):
                bytes_msg = bytes(msg, "utf-8")
                if ack_str == "y":
                    if rfm9x.send_with_ack(bytes_msg, debug=True):
                        print(
                            f"Message {bold}{i+1}{normal}: {green}Acknowledged{normal}")
                    else:
                        print(
                            f"Message {bold}{i+1}{normal}: {red}No acknowledge{normal}")
                else:
                    rfm9x.send(bytes_msg)
                    print(f"Message {bold}{i+1}{normal}: Sent")
                # time.sleep(1*(i+1))
                time.sleep(5)

            repeat_str = get_input_discrete(
                f"Repeat transmission? {bold}(y/n){normal}", ["y", "n"])
            if repeat_str == "n":
                break
