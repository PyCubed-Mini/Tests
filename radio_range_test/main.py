# Simple circuitpython receiver to verify radio hardware
import board
import busio
import digitalio
import lib.adafruit_rfm9x as adafruit_rfm9x
import time


# print formatters
bold = '\033[1m'
normal = '\033[0m'
red = '\033[31m'
green = '\033[32m'
yellow = '\033[33m'

# test messages
msg_1 = f"{bold}{red}111:{normal} A satellite or artificial satellite is an object intentionally placed into orbit in outer space."
msg_2 = f"{bold}{green}222:{normal} Except for passive satellites, most satellites have an electricity generation system for equipment on board, such as solar panels or radioisotope thermoelectric generators (RTGs)."
msg_3 = f"{bold}{red}333:{normal} Most satellites also have a method of communication to ground stations, called transponders."
msg_4 = f"{bold}{green}444:{normal} Many satellites use a standardized bus to save cost and work, the most popular of which is small CubeSats."
msg_5 = f"{bold}{red}555:{normal} Similar satellites can work together as a group, forming constellations."
msg_6 = f"{bold}{green}666:{normal} Because of the high launch cost to space, satellites are designed to be as lightweight and robust as possible."
msg_7 = f"{bold}{red}777:{normal} Most communication satellites are radio relay stations in orbit and carry dozens of transponders, each with a bandwidth of tens of megahertz."

messages = [msg_1, msg_2, msg_3, msg_4, msg_5, msg_6, msg_7]


def get_input(prompt_str, choice_values):
    print(prompt_str)
    choice = None
    while choice not in choice_values:
        choice = input(f"{choice_values} ~> ").lower()
    return choice


print(f"\n{bold}{yellow}Radio Range Test{normal}")

board_str = get_input(
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
    raise ValueError("Need to switch to output")
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
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
if board_str == "s":
    rfm9x.dio0 = radio_DIO0

# power - default is 13 dB, can go up to 23
rfm9x.tx_power = 23
print(f"\nPower = {rfm9x.tx_power} dBm")

mode_str = get_input(
    f"Operate in {bold}(r){normal}ecieve or {bold}(t){normal}ransmit mode?",
    ["r", "t"])

ack_str = get_input(
    f"Acknowledge? {bold}(y/n){normal}", ["y", "n"])

ack = (ack_str == "y")

if mode_str == "r":
    print(f"{bold}Receive{normal} mode selected, {'with acknowledge' if ack else 'no acknowledge'}")
    rfm9x.node = 0xAB  # our ID
    rfm9x.destination = 0xBA  # target's ID

    print("\n{yellow}Receiving...{normal}")
    while True:
        msg = rfm9x.receive(with_ack=ack)
        if msg is not None:
            print(msg.decode("utf-8"))
            print("\n{yellow}Receiving...{normal}")

else:
    print(f"{bold}Transmit{normal} mode selected, {'with acknowledge' if ack else 'no acknowledge'}")
    rfm9x.node = 0xBA  # our ID
    rfm9x.destination = 0xAB  # target's ID

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
        time.sleep(0.1*(i+1))
