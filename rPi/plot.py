from collections import deque
from time import sleep

import matplotlib.pyplot as plt
import numpy as np

INTERVAL = 1
HISTORY = 100

pm10 = deque(maxlen=HISTORY)
pm25 = deque(maxlen=HISTORY)
pm100 = deque(maxlen=HISTORY)
part03 = deque(maxlen=HISTORY)
part05 = deque(maxlen=HISTORY)
part10 = deque(maxlen=HISTORY)
part25 = deque(maxlen=HISTORY)
part50 = deque(maxlen=HISTORY)
part100 = deque(maxlen=HISTORY)

fig, ax = plt.subplots()

while True:
    (
        length,
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
    ) = (
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
        np.random.randint(0, 100),
    )

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

    sleep(INTERVAL)
