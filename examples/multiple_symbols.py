# ignore everything here
import sys, os
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

### !!! example starts here !!!
import time
from ticker import ticker

tick = ticker(["BINANCE:BTCUSDT", "NASDAQ:AAPL"])
tick.start()

while True:
    # Continuously outputs data for all tracked symbols, every 2 seconds
    print(tick.states) # Example: {'BINANCE:BTCUSDT': {'volume': 7247.69177, 'price': 42749.32, 'change': 238.22, 'changePercentage': 0.56, 'time': 1705390650}, 'NASDAQ:AAPL': {'volume': 40477782, 'price': 185.92, 'change': 0.33, 'changePercentage': 0.18, 'time': 1705107599}}
    time.sleep(2)