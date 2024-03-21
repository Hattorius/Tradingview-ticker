import asyncio, websockets, random, json, threading, time, sqlite3, sys, signal
from datetime import datetime

def createRandomToken(length=12):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(random.choice(chars) for i in range(length))

def getEpoch():
    return int(time.time())

class ticker:
    
    def __init__(self, symbols="BINANCE:BTCUSDT", save=False, database_name="database.db", split_symbols=False, verbose=False):
        if isinstance(symbols, str):
            symbols = [symbols]
        
        self.states = {}
        for symbol in symbols:
            self.states[symbol] = {"volume": 0, "price": 0, "change": 0, "changePercentage": 0, "time": 0}
        
        self.loop = asyncio.get_event_loop()
        self.symbols = symbols
        self.save = save
        self.connected = False
        self.databaseName = database_name
        self.splitSymbols = split_symbols
        self.cb = None
        self.db = False
        self.run = True

        self.verbose = verbose
        if verbose:
            self.saves = 0

    # Connect to database
    async def connectToDatabase(self):
        if self.save:
            self.db = sqlite3.connect(self.databaseName)
            self.createSqlite3Table()
            self.connected = True

    # Create Sqlite3 table
    def createSqlite3Table(self):
        if self.splitSymbols:
            for symbol in self.symbols:
                self.db.execute(f"""CREATE TABLE IF NOT EXISTS '{symbol}' (
                    volume real NOT NULL,
                    price real NOT NULL,
                    timestamp integer NOT NULL
                )""")
        else:
            self.db.execute("""CREATE TABLE IF NOT EXISTS ticker_data (
                volume real NOT NULL,
                price real NOT NULL,
                ticker text NOT NULL,
                timestamp integer NOT NULL
            )""")

    # Insert data into table
    def insertData(self, volume, price, ticker, time = None):
        if time is None:
            time = getEpoch()
            
        if self.cb is not None:
            self.cb(ticker, self.states[ticker])
            
        if self.save:
            if self.splitSymbols:
                self.db.execute(f"INSERT INTO '{ticker}' VALUES (?, ?, ?)", (volume, price, time))
            else:
                self.db.execute("INSERT INTO ticker_data VALUES (?, ?, ?, ?)", (volume, price, ticker, time))
            self.db.commit()

    # Connect to websocket
    async def connect(self):
        self.connection = await websockets.connect("wss://data.tradingview.com/socket.io/websocket", origin="https://www.tradingview.com")
        await self.waitForMessages()

    # Loop waiting for messages
    async def waitForMessages(self):
        await self.authenticate()
        if self.save and not self.connected:
            await self.connectToDatabase()
        while self.run:
            messages = await self.readMessage(await self.connection.recv())
            for message in messages:
                self.parseMessage(message)

    # Convert message string to object
    async def readMessage(self, message):
        messages = message.split("~m~")
        messagesObj = []
        for message in messages:
            if '{' in message or '[' in message:
                messagesObj.append(json.loads(message))
            else:
                if "~h~" in message:
                    await self.connection.send(f"~m~{len(message)}~m~{message}")

        return messagesObj

    # Convert object to message string
    def createMessage(self, name, params):
        message = json.dumps({'m': name, 'p': params})
        return f"~m~{len(message)}~m~{message}"

    # Send message
    async def sendMessage(self, name, params):
        message = self.createMessage(name, params)
        await self.connection.send(message)

    # Send authentication messages and subscribe to price & bars
    async def authenticate(self):
        self.cs = "cs_" + createRandomToken()

        await self.sendMessage("set_auth_token", ["unauthorized_user_token"])
        await self.sendMessage("chart_create_session", [self.cs, ""])

        q = createRandomToken()
        qs = "qs_" + q
        qsl = "qs_snapshoter_basic-symbol-quotes_" + q
        await self.sendMessage("quote_create_session", [qs])
        await self.sendMessage("quote_create_session", [qsl])
        await self.sendMessage("quote_set_fields", [qsl, "base-currency-logoid", "ch", "chp", "currency-logoid", "currency_code", "currency_id", "base_currency_id", "current_session", "description", "exchange", "format", "fractional", "is_tradable", "language", "local_description", "listed_exchange", "logoid", "lp", "lp_time", "minmov", "minmove2", "original_name", "pricescale", "pro_name", "short_name", "type", "typespecs", "update_mode", "volume", "variable_tick_size", "value_unit_id"])
        await self.sendMessage("quote_add_symbols", [qsl] + self.symbols)
        await self.sendMessage("quote_fast_symbols", [qs] + self.symbols)

    # this is so fricking messy
    def parseMessage(self, message):
        try:
            message['m']
        except KeyError:
            return

        if message['m'] == "qsd":
            self.forTicker(message)

    # parse ticker data
    def forTicker(self, receivedData):
        symbol = receivedData['p'][1]['n']
        data = receivedData['p'][1]['v']
        
        items = {
            "volume": "volume",
            "price": "lp",
            "changePercentage": "chp",
            "change": "ch",
            "time": "lp_time"
        }
        
        for key, data_key in items.items():
            value = data.get(data_key)
            if value is not None:
                self.states[symbol][key] = value
        
        self.insertData(self.states[symbol]["volume"], self.states[symbol]["price"], symbol, self.states[symbol]["time"])
        
        if self.verbose:
            self.saves += 1

    # send status messages every 5 seconds if enabled
    async def giveAnUpdate(self):
        while True:
            await asyncio.sleep(5)
            print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}: Watching {len(self.symbols)} tickers → received {self.saves} updates")
            self.saves = 0

    # start ticker in new thread
    def start(self):
        self.loop = asyncio.new_event_loop()
        def _start(loop):
            asyncio.set_event_loop(loop)
            self.run = True
            self.task = loop.create_task(self.connect())
            if self.verbose:
                self.updateTask = loop.create_task(self.giveAnUpdate())
            loop.run_forever()

        t = threading.Thread(target=_start, args=(self.loop,))
        t.start()
        self.thread = t

        # register signal handlers
        signal.signal(signal.SIGINT, self.cleanup_on_exit)  # SIGINT (Ctrl+C)
        signal.signal(signal.SIGTERM, self.cleanup_on_exit) # SIGTERM (termination signal)

    # stop it :(
    def stop(self):
        self.run = False
        self.task.cancel()
        if self.verbose:
            self.updateTask.cancel()
        self.loop.stop()
        self.thread.join()

        if self.db:
            self.db.close()

    def cleanup_on_exit(self, a, b):
        print("Closing (can take a few seconds)")

        self.stop()
        sys.exit(0)
