#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import subprocess
import sys
from prometheus_client import start_http_server, Gauge, Counter

# Create Prometheus metrics to track bitcoind stats.
BASE_CPU_TEMP = Gauge("base_cpu_temp", "CPU temperature")
BASE_FAN_SPEED = Gauge("base_fan_speed", "Fan speed in %")

# systemd status: 0 = running / 3 = inactive
BASE_SYSTEMD_BITCOIND = Gauge("base_systemd_bitcoind", "Systemd unit status for Bitcoin Core")
BASE_SYSTEMD_ELECTRS = Gauge("base_systemd_electrs", "Systemd unit status for Electrs")
BASE_SYSTEMD_LIGHTNINGD = Gauge("base_systemd_lightningd", "Systemd unit status for c-lightning")
BASE_SYSTEMD_PROMETHEUS = Gauge("base_systemd_prometheus", "Systemd unit status for Prometheus")
BASE_SYSTEMD_GRAFANA = Gauge("base_systemd_grafana", "Systemd unit status for Grafana")


def readFile(filepath):
    args = [filepath]
    with open(filepath) as f:
        value = f.readline()

    return value


def getSystemdStatus(unit):
    try:
        subprocess.check_output(["systemctl", "is-active", unit])
        return 0
    except subprocess.CalledProcessError as e:
        print(unit, e.returncode, e.output)
        return e.returncode


def main():
    # Start up the server to expose the metrics.
    start_http_server(8400)
    while True:
        BASE_CPU_TEMP.set(readFile("/sys/class/thermal/thermal_zone0/temp"))
        BASE_FAN_SPEED.set(readFile("/sys/class/hwmon/hwmon0/pwm1"))

        BASE_SYSTEMD_BITCOIND.set(int(getSystemdStatus("bitcoind")))
        BASE_SYSTEMD_ELECTRS.set(int(getSystemdStatus("electrs")))
        BASE_SYSTEMD_LIGHTNINGD.set(int(getSystemdStatus("lightningd")))
        BASE_SYSTEMD_PROMETHEUS.set(int(getSystemdStatus("prometheus")))
        BASE_SYSTEMD_GRAFANA.set(int(getSystemdStatus("grafana-server")))

        time.sleep(10)


if __name__ == "__main__":
    main()
