# ignore everything here
import sys, os
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# example starts here
import time
from ticker import ticker

# handle ticker data as soon as it comes
def handleTicker(ticker, data):
    print(f"Ticker update! {ticker}: {data}")
    pass

tick = ticker("BINANCE:BTCUSDT")
tick.cb = handleTicker
tick.start()

while True: # Just to make sure the thread doesn't die on me
    time.sleep(1)