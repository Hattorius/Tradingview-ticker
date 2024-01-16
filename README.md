![Visitors](https://visitor-badge.laobi.icu/badge?page_id=Hattorius.Tradingview-ticker)
# Tradingview-ticker
This Python tool reverse-engineers the connection to the TradingView ticker, allowing for real-time updates on price and volume via a WebSocket connection. It's specifically developed and tested on Python 3.11.6.

> **Important:** Ensure the main thread is continuously running, otherwise, the program will terminate. Use `while True: pass` if needed.

## Table of contents
* [Introduction](#introduction)
* [Features](#features)
* [Prerequisites](#prerequisites)
* [Installing](#installing)
* [Quick example](#quick-example)
* [Documentation](#documentation)
* [License](#license)

## Introduction
The "Tradingview-ticker" is a specialized tool designed for enthusiasts and professionals in the financial markets who require real-time access to market data. This Python-based utility serves as a bridge, connecting users directly to TradingView's extensive ticker system. It enables users to track and analyze market tickers from TradingView in real-time, integrating this valuable data seamlessly into their own programs and trading strategies.

At its core, the "Tradingview-ticker" reverse-engineers the connection to the TradingView ticker, establishing a stable and efficient WebSocket connection. This allows for the live streaming of price and volume updates, a critical feature for those who rely on up-to-the-second market data. Whether you are building a sophisticated trading algorithm, a data analysis tool, or simply need live market data for informed decision-making, this tool provides a reliable and easy-to-use solution.

Developed with a focus on ease of use, stability, and flexibility, "Tradingview-ticker" is not just about providing data; it's about opening up a world of possibilities for financial analysis and algorithmic trading. By leveraging the power of Python and the comprehensive data from TradingView, users can create more informed, data-driven strategies and applications.

Whether you're a hobbyist experimenting with market data, a researcher analyzing trends, or a developer building the next big trading algorithm, "Tradingview-ticker" is your gateway to harnessing the power of real-time financial data from one of the most popular trading platforms available.

- ChatGPT

## Features
* **Persistent WebSocket Connection**: Maintains a live connection to TradingView for continuous data streaming.
* **Multi-Ticker Monitoring**: Ability to track multiple tickers simultaneously.
* **No Rate Limiting**: Efficiently designed to avoid cooldowns or rate limits.
* **SQLite3 Integration**: Enables saving ticker data locally for analysis.
* **User-Friendly**: Designed for ease of use without sacrificing functionality.
* **Reliability**: Proven stability, running seamlessly during extensive testing.

## Prerequisites
* [Python 3.8+](https://www.python.org/downloads/)

For Windows users, ensure Python is added to your PATH. Guidance available [here](https://superuser.com/a/143121).

## Installing
Run the following command in your project directory:
```
# Linux/macOS
python3 -m pip install -r requirements.txt

# Windows
py -3 -m pip install -r requirements.txt
```

## Quick Example
Use the library to track Bitcoin prices on Binance:

```py
import time
from ticker import ticker

tick = ticker("BINANCE:BTCUSDT")
tick.start()

while True:
    # Prints price and volume every 2 seconds
    print(tick.states) # Example: {'BINANCE:BTCUSDT': {'volume': 7234.88273, 'price': 42759.18, 'change': 248.08, 'changePercentage': 0.58, 'time': 1705390590}}
    time.sleep(2)
```

### Multiple Symbols
Track multiple symbols like Bitcoin and Apple:

```py
import time
from ticker import ticker

tick = ticker(["BINANCE:BTCUSDT","NASDAQ:AAPL"])
tick.start()

while True:
    # Continuously outputs data for all tracked symbols, every 2 seconds
    print(tick.states) # Example: {'BINANCE:BTCUSDT': {'volume': 7247.69177, 'price': 42749.32, 'change': 238.22, 'changePercentage': 0.56, 'time': 1705390650}, 'NASDAQ:AAPL': {'volume': 40477782, 'price': 185.92, 'change': 0.33, 'changePercentage': 0.18, 'time': 1705107599}}
    time.sleep(2)
```

### Ticker callback
In addition to simply retrieving and storing data, "Tradingview-ticker" also allows for real-time data processing through a callback mechanism. This feature is particularly useful for users who wish to perform immediate analysis, display, or further processing of ticker data as soon as it's received. Below is an example of how to implement a callback function:
```py
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
```

## Documentation
Further details and API reference can be found [here](https://github.com/Hattorius/Tradingview-ticker/wiki/API-Reference).

### SQLite3 Database Integration
The "Tradingview-ticker" includes an integration with SQLite3, providing a convenient way to store and manage the ticker data. This feature allows users to save the real-time data into a local database, enabling further data analysis and historical data tracking. Below are the details on how this feature works and how it can be configured:

To enable data saving, follow the instructions in the documentation. Once set up, all the ticker information you track will be automatically saved into the SQLite3 database.

#### Database Structure with `split_symbols`
**When `split_symbols` is Enabled**: If this option is activated, the ticker data will be stored in separate tables, each named after its respective ticker. For example, if you're tracking `BINANCE:BTCUSDT`, the table will be named `BINANCE:BTCUSDT`.

Fields in table: Each table will contain the following fields:
- `volume`: The trading volume (data type: `real`).
- `price`: The current price (data type: `real`).
- `timestamp`: The timestamp of the data (data type: `integer`, formatted as an EPOCH timestamp).

#### Database Structure without `split_symbols`
**When split_symbols is Disabled** (default setting): In this mode, the data for all tickers will be consolidated into a single table named `ticker_data``.

Fields in `ticker_data` table: The unified table will include:
- `volume`: The trading volume (data type: `real`).
- `price`: The current price (data type: `real`).
- `timestamp`: The timestamp of the data (data type: `integer`, formatted as an EPOCH timestamp).
- `ticker`: The name of the ticker (data type: `text`, e.g., `BINANCE:BTCUSDT`).

## License
This project is licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE) file for details.
