import os
import struct
from collections import deque
from random import randint
from time import sleep, time

DRY_RUN = os.getenv("DRY_RUN")

import matplotlib.pyplot as plt
import requests

# Setup channels
SET = 23
RESET = 24
TX = 14
RX = 15

if not DRY_RUN:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup([SET, RESET], GPIO.OUT, initial=GPIO.HIGH)
    print(f"Running on {GPIO.RPI_INFO}!")


import serial

HISTORY = 1440
INTERVAL = 60
RESET_EVERY = 1
COUNT = 0

START1 = b"\x42"
START2 = b"\x4d"
LOG = "log.csv"

METRICS_ENDPOINT = os.getenv("METRICS_ENDPOINT")

pm10 = deque(maxlen=HISTORY)
pm25 = deque(maxlen=HISTORY)
pm100 = deque(maxlen=HISTORY)
part03 = deque(maxlen=HISTORY)
part05 = deque(maxlen=HISTORY)
part10 = deque(maxlen=HISTORY)
part25 = deque(maxlen=HISTORY)
part50 = deque(maxlen=HISTORY)
part100 = deque(maxlen=HISTORY)


def reset():
    if DRY_RUN:
        return
    # Reset
    GPIO.output(RESET, 0)
    sleep(1)
    GPIO.output(RESET, 1)


if not DRY_RUN:
    serial0 = serial.Serial("/dev/serial0", 9600)

f = open(LOG, "a")

fig, (ax, ax2) = plt.subplots(2)

while True:
    COUNT += 1
    if COUNT % RESET_EVERY == 0:
        reset()

    if not DRY_RUN:
        # Wait for the start characters
        while b1 := serial0.read() != START1:
            continue

        if b2 := serial0.read() != START2:
            continue

    if not DRY_RUN:
        b = serial0.read(30)
    else:
        b = struct.pack(
            ">15h",
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
        )
    (
        lenght,
        pm10_standard,
        pm25_standard,
        pm100_standard,
        pm10_env,
        pm25_env,
        pm100_env,
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
    ax2.clear()

    ax2.plot(pm10, label="PM10")
    ax2.plot(pm25, label="PM2.5")
    ax2.plot(pm100, label="PM100")

    ax.plot(part03, label="Particles > 0.3um")
    ax.plot(part05, label="Particles > 0.5um")
    ax.plot(part10, label="Particles > 1.0um")
    ax.plot(part25, label="Particles > 2.5um")
    ax.plot(part50, label="Particles > 5.0um")
    ax.plot(part100, label="Particles > 10.0um")

    ax.legend()
    ax2.legend()

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
        pm100_env,
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

    ts = int(time()/INTERVAL) * INTERVAL
    response = requests.post(
        METRICS_ENDPOINT,
        json=[
            {
                "name": "air.quality.pm10.standard",
                "interval": INTERVAL,
                "value": pm10_standard,
                "time": ts
            },
            {
                "name": "air.quality.pm25.standard",
                "interval": INTERVAL,
                "value": pm25_standard,
                "time": ts
            },
            {
                "name": "air.quality.pm100.standard",
                "interval": INTERVAL,
                "value": pm100_standard,
                "time": ts
            },
            {
                "name": "air.quality.pm10.env",
                "interval": INTERVAL,
                "value": pm10_env,
                "time": ts
            },
            {
                "name": "air.quality.pm25.env",
                "interval": INTERVAL,
                "value": pm25_env,
                "time": ts
            },
            {
                "name": "air.quality.pm100.env",
                "interval": INTERVAL,
                "value": pm100_env,
                "time": ts
            },
            {
                "name": "air.quality.part.03",
                "interval": INTERVAL,
                "value": part_03um,
                "time": ts
            },
            {
                "name": "air.quality.part.05",
                "interval": INTERVAL,
                "value": part_05um,
                "time": ts
            },
            {
                "name": "air.quality.part.10",
                "interval": INTERVAL,
                "value": part_10um,
                "time": ts
            },
            {
                "name": "air.quality.part.25",
                "interval": INTERVAL,
                "value": part_25um,
                "time": ts
            },
            {
                "name": "air.quality.part.50",
                "interval": INTERVAL,
                "value": part_50um,
                "time": ts
            },
            {
                "name": "air.quality.part.100",
                "interval": INTERVAL,
                "value": part_100um,
                "time": ts
            },
        ],
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('METRICS_USER')}:{os.getenv('METRICS_API_KEY')}",
        },
    )
    print(response.status_code)

    sleep(INTERVAL)
