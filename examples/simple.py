# ignore everything here
import sys, os
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# example starts here
import time
from ticker import ticker

tick = ticker("BINANCE:BTCUSDT")
tick.start()

while True: # Print out prices & volumes every 2 seconds
    print(tick.states) # Example: {'BINANCE:BTCUSDT': {'volume': 2089.98057, 'price': 67715.07, 'change': 189.24, 'changePercentage': 0.28}}
    time.sleep(2)