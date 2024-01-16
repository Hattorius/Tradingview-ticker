# ignore everything here
import sys, os
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

### !!! example starts here !!!
import time
from ticker import ticker

tick = ticker("BINANCE:BTCUSDT")
tick.start()

while True:
    # Prints price and volume every 2 seconds
    print(tick.states) # Example: {'BINANCE:BTCUSDT': {'volume': 7234.88273, 'price': 42759.18, 'change': 248.08, 'changePercentage': 0.58, 'time': 1705390590}}
    time.sleep(2)