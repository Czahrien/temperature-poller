from glob import glob
from datetime import datetime
import requests
from syslog import syslog
import config


def main():
    # The w1_gpio and w1_therm create devices in this path and put the dat into w1_slave
    # Example reading:
    # /sys/bus/w1/devices/28-0114535d9aaa/w1_slave
    # 66 00 4b 46 7f ff 0c 10 ba : crc=ba YES
    # 66 00 4b 46 7f ff 0c 10 ba t=6375
    for file in glob("/sys/bus/w1/devices/*/w1_slave"):
        parts = file.split("/")
        f = open(file)
        contents = f.read()
        lines = contents.split("\n")
        f.close()

        reading = {
            'date': datetime.utcnow().isoformat() + 'Z',
            "device":  parts[-2],
            "crc_pass": 'YES' == lines[0].split(" ")[-1],
            "temperature": int(lines[1].split("=")[-1]),
            "raw_data": contents
        }
        print(reading)

        try:
            resp = requests.post(**config.API_ENDPOINT, json=reading)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            syslog(str(err))
            syslog(str(reading))
        except requests.exceptions.ConnectionError as err:
            syslog(str(err))
            syslog(str(reading))
        except requests.exceptions.Timeout as err:
            syslog(str(err))
            syslog(str(reading))
        except requests.exceptions.RequestException as err:
            syslog(str(err))
            syslog(str(reading))


if __name__ == '__main__':
    main()
