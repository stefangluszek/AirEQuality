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

MEASURE_INTERVAL = 1
SEND_EVERY = 60
RESET_EVERY = 600
COUNT = 0

START1 = b"\x42"
START2 = b"\x4d"

METRICS_ENDPOINT = os.getenv("METRICS_ENDPOINT")

pm10_s = deque(maxlen=SEND_EVERY)
pm25_s = deque(maxlen=SEND_EVERY)
pm100_s = deque(maxlen=SEND_EVERY)
pm10_e = deque(maxlen=SEND_EVERY)
pm25_e = deque(maxlen=SEND_EVERY)
pm100_e = deque(maxlen=SEND_EVERY)
part03 = deque(maxlen=SEND_EVERY)
part05 = deque(maxlen=SEND_EVERY)
part10 = deque(maxlen=SEND_EVERY)
part25 = deque(maxlen=SEND_EVERY)
part50 = deque(maxlen=SEND_EVERY)
part100 = deque(maxlen=SEND_EVERY)


def reset():
    if DRY_RUN:
        return
    # Reset
    GPIO.output(RESET, 0)
    sleep(1)
    GPIO.output(RESET, 1)


if not DRY_RUN:
    serial0 = serial.Serial("/dev/serial0", 9600)

fig, (ax, ax2) = plt.subplots(2)

while True:
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

    pm10_s.append(pm10_standard)
    pm25_s.append(pm25_standard)
    pm100_s.append(pm100_standard)
    pm10_e.append(pm10_env)
    pm25_e.append(pm25_env)
    pm100_e.append(pm100_env)
    part03.append(part_03um)
    part05.append(part_05um)
    part10.append(part_10um)
    part25.append(part_25um)
    part50.append(part_50um)
    part100.append(part_100um)

    if COUNT % SEND_EVERY == 0:
        pm10_standard = sum(pm10_s) / len(pm10_s)
        pm25_standard = sum(pm25_s) / len(pm25_s)
        pm100_standard = sum(pm100_s) / len(pm100_s)
        pm10_env = sum(pm10_e) / len(pm10_e)
        pm25_env = sum(pm25_e) / len(pm25_e)
        m100_env = sum(pm100_e) / len(pm100_e)
        part_03um = sum(part03) / len(part03)
        part_05um = sum(part05) / len(part05)
        part_25um = sum(part25) / len(part25)
        part_50um = sum(part50) / len(part50)
        part_100um = sum(part100) / len(part100)

        ax.clear()
        ax2.clear()

        ax2.plot(pm10_s, label="PM10")
        ax2.plot(pm25_s, label="PM2.5")
        ax2.plot(pm100_s, label="PM100")

        ax.plot(part03, label="Particles > 0.3um")
        ax.plot(part05, label="Particles > 0.5um")
        ax.plot(part10, label="Particles > 1.0um")
        ax.plot(part25, label="Particles > 2.5um")
        ax.plot(part50, label="Particles > 5.0um")
        ax.plot(part100, label="Particles > 10.0um")

        ax.legend()
        ax2.legend()

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

        ts = int(time() / SEND_EVERY * MEASURE_INTERVAL) * SEND_EVERY
        INTERVAL = SEND_EVERY * MEASURE_INTERVAL
        try:
            response = requests.post(
                METRICS_ENDPOINT,
                json=[
                    {
                        "name": "air.quality.pm10.standard",
                        "interval": INTERVAL,
                        "value": pm10_standard,
                        "time": ts,
                    },
                    {
                        "name": "air.quality.pm25.standard",
                        "interval": INTERVAL,
                        "value": pm25_standard,
                        "time": ts,
                    },
                    {
                        "name": "air.quality.pm100.standard",
                        "interval": INTERVAL,
                        "value": pm100_standard,
                        "time": ts,
                    },
                    {
                        "name": "air.quality.pm10.env",
                        "interval": INTERVAL,
                        "value": pm10_env,
                        "time": ts,
                    },
                    {
                        "name": "air.quality.pm25.env",
                        "interval": INTERVAL,
                        "value": pm25_env,
                        "time": ts,
                    },
                    {
                        "name": "air.quality.pm100.env",
                        "interval": INTERVAL,
                        "value": pm100_env,
                        "time": ts,
                    },
                    {
                        "name": "air.quality.part.03",
                        "interval": INTERVAL,
                        "value": part_03um,
                        "time": ts,
                    },
                    {
                        "name": "air.quality.part.05",
                        "interval": INTERVAL,
                        "value": part_05um,
                        "time": ts,
                    },
                    {
                        "name": "air.quality.part.10",
                        "interval": INTERVAL,
                        "value": part_10um,
                        "time": ts,
                    },
                    {
                        "name": "air.quality.part.25",
                        "interval": INTERVAL,
                        "value": part_25um,
                        "time": ts,
                    },
                    {
                        "name": "air.quality.part.50",
                        "interval": INTERVAL,
                        "value": part_50um,
                        "time": ts,
                    },
                    {
                        "name": "air.quality.part.100",
                        "interval": INTERVAL,
                        "value": part_100um,
                        "time": ts,
                    },
                ],
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.getenv('METRICS_USER')}:{os.getenv('METRICS_API_KEY')}",
                },
            )
        except Exception as e:
            print("Posting metrics failed: ", e) 
        print(response.status_code)

    COUNT += 1
    plt.pause(MEASURE_INTERVAL)
