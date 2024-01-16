import board
import busio
import digitalio
import adafruit_rfm69

import time
from micropython import const

### Configurations
radio_freq = 315.0  # float in MHz
tesla_sync_word = "\x8A\xCB"
tesla_charge_port_signal = "\xAA\xAA\xAA\x8A\xCB\x32\xCC\xCC\xCB\x4D\x2D\x4A\xD3\x4C\xAB\x4B\x15\x96\x65\x99\x99\x96\x9A\x5A\x95\xA6\x99\x56\x96\x2B\x2C\xCB\x33\x33\x2D\x34\xB5\x2B\x4D\x32\xAD\x28"

### Setup Code
print("...")
print("Configuring LED..")
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = False  # turn it off to start

print("Configuring radio for {}MHz..".format(radio_freq))
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.RFM69_CS)
reset = digitalio.DigitalInOut(board.RFM69_RST)
rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, sync_word=tesla_sync_word, preamble_length=3, frequency=radio_freq)
print("DONE")

#ok = rfm69.send(tesla_charge_port_signal) # doesn't work cause library adds data and headers
def send_message(rfm69_object) -> bool:
        """stolen directly from adafruit_rfm69.RFM69 send function and tweaked to be more direct"""
        # hard-coded to use tesla_charge_port_signal global variable

        # Stop receiving to clear FIFO and keep it clear.
        rfm69_object.idle()
        # Write payload to transmit fifo
        rfm69_object._write_from(const(0x00), tesla_charge_port_signal)
        # Turn on transmit mode to send out the packet.
        rfm69_object.transmit()
        # Wait for packet sent interrupt with explicit polling (not ideal but
        # best that can be done right now without interrupts).
        timed_out = adafruit_rfm69.check_timeout(rfm69_object.packet_sent, rfm69_object.xmit_timeout)
        return not timed_out

while True:
    print("Waiting 5sec")
    time.sleep(5)
    print("Sending message 10 times in a row")
    for i in range(0, 10):
        led.value = True
        send_message(rfm69)
        print("{} ".format(i+1), end="")
        led.value = False
    print("Done")

### action code
print("Waiting to receving something in the next 60sec")
while True:
    recv_value = rfm69.receive(timeout=60.0, with_header=True)  # blocks until reciving a packet
    if recv_value is not None:
        print(recv_value)
    else:
        print("Didn't get anything.. :(")
    print("listnening again..")
