import struct
from collections import deque
from time import sleep, time

import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
import serial

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

print(f"Running on {GPIO.RPI_INFO}!")

# Setup channels
SET = 23
RESET = 24
TX = 14
RX = 15

HISTORY = 1440
INTERVAL = 60

START1 = b"\x42"
START2 = b"\x4d"
LOG = "log.csv"

pm10 = deque(maxlen=HISTORY)
pm25 = deque(maxlen=HISTORY)
pm100 = deque(maxlen=HISTORY)
part03 = deque(maxlen=HISTORY)
part05 = deque(maxlen=HISTORY)
part10 = deque(maxlen=HISTORY)
part25 = deque(maxlen=HISTORY)
part50 = deque(maxlen=HISTORY)
part100 = deque(maxlen=HISTORY)


GPIO.setup([SET, RESET], GPIO.OUT, initial=GPIO.HIGH)

serial = serial.Serial("/dev/serial0", 9600)
f = open(LOG, "a")

fig, ax = plt.subplots()

while True:
    # Wait for the start characters
    while b1 := serial.read() != START1:
        continue

    if b2 := serial.read() != START2:
        continue

    b = serial.read(30)
    (
        lenght,
        pm10_standard,
        pm25_standard,
        pm100_standard,
        pm10_env,
        pm25_env,
        pm_100_env,
        part_03um,
        part_05um,
        part_10um,
        part_25um,
        part_50um,
        part_100um,
        reserved,
        checksum,
    ) = struct.unpack(">15H", b)

    pm10.append(pm10_standard)
    pm25.append(pm25_standard)
    pm100.append(pm100_standard)
    part03.append(part_03um)
    part05.append(part_05um)
    part10.append(part_10um)
    part25.append(part_25um)
    part50.append(part_50um)
    part100.append(part_100um)

    ax.clear()
    ax.plot(pm10, label="PM10")
    ax.plot(pm25, label="PM2.5")
    ax.plot(pm100, label="PM100")
    ax.plot(part03, label="Particles > 0.3um")
    ax.plot(part05, label="Particles > 0.5um")
    ax.plot(part10, label="Particles > 1.0um")
    ax.plot(part25, label="Particles > 2.5um")
    ax.plot(part50, label="Particles > 5.0um")
    ax.plot(part100, label="Particles > 10.0um")
    ax.legend()

    plt.pause(INTERVAL)

    print("####### AIR QUALITY #############")
    print(f"PM1.0: {pm10_standard}uq/m3")
    print(f"PM2.5: {pm25_standard}uq/m3")
    print(f"PM10: {pm100_standard}uq/m3")
    print(f"particles over 0.3um: {part_03um} in 0.1L of air")
    print(f"particles over 0.5um: {part_05um} in 0.1L of air")
    print(f"particles over 1.0um: {part_10um} in 0.1L of air")
    print(f"particles over 2.5um: {part_25um} in 0.1L of air")
    print(f"particles over 5.0um: {part_50um} in 0.1L of air")
    print(f"particles over 10.0um: {part_100um} in 0.1L of air")
    print()

    fields = [
        int(time()),
        lenght,
        pm10_standard,
        pm25_standard,
        pm100_standard,
        pm10_env,
        pm25_env,
        pm_100_env,
        part_03um,
        part_05um,
        part_10um,
        part_25um,
        part_50um,
        part_100um,
        reserved,
        checksum,
    ]

    line = ",".join(str(f) for f in fields)

    f.write(line + "\n")

    sleep(INTERVAL)
