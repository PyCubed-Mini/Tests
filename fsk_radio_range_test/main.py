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

messages = [msg_1]


def get_input_discrete(prompt_str, choice_values):
    print(prompt_str)
    choice = None

    choice_values_str = "("
    for i, _ in enumerate(choice_values):
        choice_values_str += f"{choice_values[i]}"
        if i < len(choice_values) - 1:
            choice_values_str += ", "
    choice_values_str += ")"

    while choice not in choice_values:
        choice = input(f"{choice_values_str} ~> ").lower()
    return choice


def set_param_from_input_discrete(param, prompt_str, choice_values, allow_default=False):

    # add "enter" as a choice
    choice_values = [""] + choice_values if allow_default else choice_values
    prompt_str = prompt_str + \
        " (enter to skip):" if allow_default else prompt_str

    choice = get_input_discrete(prompt_str, choice_values)

    if choice == "":
        return param
    else:
        return int(choice)


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

        if float(choice) > choice_range[0] and float(choice) < choice_range[1]:
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
    f"Select the board {bold}(s){normal}atellite, {bold}(f){normal}eather, {bold}(r){normal}aspberry pi",
    ["s", "f", "r"]
)

if board_str == "s":
    # pocketqube
    CS = digitalio.DigitalInOut(board.RF_CS)
    RESET = digitalio.DigitalInOut(board.RF_RST)
    CS.switch_to_output(value=True)
    RESET.switch_to_output(value=True)

    radio_DIO0 = digitalio.DigitalInOut(board.RF_IO0)
    radio_DIO0.switch_to_input()
    radio_DIO1 = digitalio.DigitalInOut(board.RF_IO1)
    radio_DIO1.switch_to_input()

    print(f"{bold}{green}Satellite{normal} selected")
elif board_str == "f":
    # feather
    CS = digitalio.DigitalInOut(board.D5)
    RESET = digitalio.DigitalInOut(board.D6)
    CS.switch_to_output(value=True)
    RESET.switch_to_output(value=True)

    raise ValueError("Feather: untested")
    print(f"{bold}{green}Feather{normal} selected")
else:  # board_str == "r"
    # raspberry pi
    CS = digitalio.DigitalInOut(board.CE1)
    RESET = digitalio.DigitalInOut(board.D25)
    print(f"{bold}{green}Raspberry Pi{normal} selected")

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
RADIO_FREQ_MHZ = 433.0
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ, crc=False)
if board_str == "s":
    rfm9x.dio0 = radio_DIO0

# RFM radio configuration

param_str = get_input_discrete(
    f"Change radio parameters? {bold}(y/n){normal}", ["y", "n"])

# start by setting the defaults
rfm9x.frequency_mhz = 433.0
rfm9x.tx_power = 23
rfm9x.bitrate = 1200
rfm9x.frequency_deviation = 5000
rfm9x.rx_bandwidth = 50.0
timeout = rfm9x.receive_timeout
rfm9x.preamble_length = 16

if param_str == "y":
    rfm9x.frequency_mhz = set_param_from_input_range(rfm9x.frequency_mhz, f"Frequency (currently {rfm9x.frequency_mhz} MHz)",
                                                     [240.0, 960.0], allow_default=True)
    rfm9x.tx_power = set_param_from_input_discrete(rfm9x.tx_power, f"Power (currently {rfm9x.tx_power} dB)",
                                                   [f"{i}" for i in range(5, 24)], allow_default=True)
    rfm9x.bitrate = set_param_from_input_range(rfm9x.bitrate, f"Bitrate (currently {rfm9x.bitrate} bps)",
                                               [500, 300000], allow_default=True)
    rfm9x.frequency_deviation = set_param_from_input_range(rfm9x.frequency_deviation, f"Frequency deviation (currently {rfm9x.frequency_deviation})",
                                                           [600, 200000], allow_default=True)
    rfm9x.rx_bandwidth = set_param_from_input_discrete(rfm9x.rx_bandwidth, f"Receiver filter bandwidth (currently {rfm9x.rx_bandwidth})",
                                                       list(rfm9x._bw_bins_kHz), allow_default=True)
    rfm9x.lna_gain = set_param_from_input_discrete(rfm9x.lna_gain, f"LNA Gain - [max = 1, min = 6] (currently {rfm9x.lna_gain})",
                                                   [f"{i}" for i in range(1, 7)], allow_default=True)
    rfm9x.preamble_length = set_param_from_input_range(rfm9x.preamble_length, f"Preamble length (currently {rfm9x.preamble_length})",
                                                       [3, 2**16], allow_default=True)
    timeout = set_param_from_input_range(timeout, f"Timeout (currently {timeout} s)",
                                         [0.0, 1000.0], allow_default=True)

print(f"{yellow}{bold}Radio Parameters:{normal}")
print(f"\tFrequency = {rfm9x.frequency_mhz} MHz")
print(f"\tPower = {rfm9x.tx_power} dBm")
print(f"\tBitrate = {rfm9x.bitrate} Hz")
print(f"\tFrequency Deviation = {rfm9x.frequency_deviation}")
print(f"\tRX filter bandwidth = {rfm9x.rx_bandwidth}")
print(f"\tLNA Gain [max = 1, min = 6] = {rfm9x.lna_gain}")
print(f"\tPreamble Length = {rfm9x.preamble_length}")
print(f"\tTimeout = {timeout} s")

mode_str = get_input_discrete(
    f"Operate in {bold}(r){normal}ecieve or {bold}(t){normal}ransmit mode?",
    ["r", "t"])

ack_str = get_input_discrete(
    f"Acknowledge? {bold}(y/n){normal}", ["y", "n"])

ack = (ack_str == "y")

if mode_str == "r":
    print(f"{bold}Receive{normal} mode selected, {'with acknowledge' if ack else 'no acknowledge'}")
    rfm9x.node = 0xAB  # our ID
    rfm9x.destination = 0xBA  # target's ID

    print(f"\n{yellow}Receiving...{normal}")
    while True:
        msg = rfm9x.receive(with_ack=ack, debug=True, timeout=timeout)
        if msg is not None:
            print(f"(RSSI: {rfm9x.last_rssi} | FEI: {rfm9x.frequency_error})\t" +
                  msg.decode("utf-8", "backslashreplace"))

else:
    print(f"{bold}Transmit{normal} mode selected, {'with acknowledge' if ack else 'no acknowledge'}")
    rfm9x.node = 0xBA  # our ID
    rfm9x.destination = 0xAB  # target's ID

    while True:
        for i, msg in enumerate(messages):
            bytes_msg = bytes(msg, "utf-8")
            if ack_str == "y":
                if rfm9x.send_with_ack(bytes_msg):
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