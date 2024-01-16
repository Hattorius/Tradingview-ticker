# ignore everything here
import sys, os
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

### !!! example starts here !!!
import time
from ticker import ticker

# Define a callback function to handle incoming ticker data
def handleTicker(ticker_name, data):
    # data contains information such as volume, price, change, etc.
    print(f"Ticker update! {ticker_name}: {data}")
    pass

# Initialize the ticker object for a specific ticker
tick = ticker("BINANCE:BTCUSDT")

# Assign the callback function
tick.cb = handleTicker

# Start the ticker to receive data
tick.start()

# Run an infinite loop to keep the main thread alive
while True:
    time.sleep(1)