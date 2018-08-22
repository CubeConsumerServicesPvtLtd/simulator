from datetime import datetime
from simulator import simulator


if __name__ == "__main__":
    dt = datetime.strptime('2018-06-22 12:41:02', "%Y-%m-%d %H:%M:%S")
    print(simulator.getdate(1, dt, 'EDGCGP-GR'))

