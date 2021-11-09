import asyncio, websockets, random, json, threading, time, sqlite3
from datetime import datetime

def createRandomToken(length=12):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for i in range(length))

def getEpoch():
    return int(time.time())

class ticker:
    
    def __init__(self, symbols='BINANCE:BTCUSDT', save=False, database_name='database.db', split_symbols=False, verbose=False):
        self.loop = asyncio.get_event_loop()
        if isinstance(symbols, str):
            symbols = ['BINANCE:BTCUSDT']
        self.symbols = symbols
        self.states = {}
        for symbol in symbols:
            self.states[symbol] = {'volume': 0, 'price': 0, 'change': 0, 'changePercentage': 0}
        self.save = save
        self.connected = False
        self.database_name = database_name
        self.split_symbols = split_symbols

        self.verbose = verbose
        if verbose:
            self.saves = 0

    # Connect to database
    async def connectToDatabase(self):
        if self.save:
            self.db = sqlite3.connect(self.database_name)
            self.createSqlite3Table()
            self.connected = True

    # Create Sqlite3 table
    def createSqlite3Table(self):
        if self.split_symbols:
            for symbol in self.symbols:
                self.db.execute("""CREATE TABLE IF NOT EXISTS '{}' (
                    volume real NOT NULL,
                    price real NOT NULL,
                    timestamp integer NOT NULL
                )""".format(symbol))
        else:
            self.db.execute("""CREATE TABLE IF NOT EXISTS ticker_data (
                volume real NOT NULL,
                price real NOT NULL,
                ticker text NOT NULL,
                timestamp integer NOT NULL
            )""")

    # Insert data into table
    def insertData(self, volume, price, ticker):
        if self.save:
            if self.split_symbols:
                self.db.execute("INSERT INTO '"+ticker+"' VALUES (?, ?, ?)", (volume, price, getEpoch()))
            else:
                self.db.execute("INSERT INTO ticker_data VALUES (?, ?, ?, ?)", (volume, price, ticker, getEpoch()))
            self.db.commit()

    # Connect to websocket
    async def connect(self):
        self.connection = await websockets.connect("wss://data.tradingview.com/socket.io/websocket", origin="https://www.tradingview.com")
        await self.waitForMessages()
        await asyncio.Future()

    # Loop waiting for messages
    async def waitForMessages(self):
        await self.authenticate()
        if self.save and not self.connected:
            await self.connectToDatabase()
        while True:
            messages = await self.readMessage(await self.connection.recv())
            for message in messages:
                self.parseMessage(message)

    # Convert message string to object
    async def readMessage(self, message):
        messages = message.split('~m~')
        messagesObj = []
        for message in messages:
            if '{' in message or '[' in message:
                messagesObj.append(json.loads(message))
            else:
                if '~h~' in message:
                    await self.connection.send("~m~{}~m~{}".format(len(message), message))

        return messagesObj

    # Convert object to message string
    def createMessage(self, name, params):
        message = json.dumps({'m': name, 'p': params})
        return "~m~{}~m~{}".format(len(message), message)

    # Send message
    async def sendMessage(self, name, params):
        message = self.createMessage(name, params)
        await self.connection.send(message)

    # Send authentication messages and subscribe to price & bars
    async def authenticate(self):
        self.cs = 'cs_' + createRandomToken()

        await self.sendMessage("set_auth_token", ["unauthorized_user_token"])
        await self.sendMessage("chart_create_session", [self.cs, ""])
        for symbol in self.symbols:
            qs = 'qs_' + createRandomToken()
            await self.sendMessage("quote_create_session", [qs])
            await self.sendMessage("quote_set_fields", [qs, "ch","chp","current_session","description","local_description","language","exchange","fractional","is_tradable","lp","lp_time","minmov","minmove2","original_name","pricescale","pro_name","short_name","type","update_mode","volume","currency_code","rchp","rtc"])
            await self.sendMessage("quote_add_symbols",[qs, symbol, {"flags":['force_permission']}])
            await self.sendMessage("quote_fast_symbols", [qs, symbol])
        return 0

    # this is so fricking messy
    def parseMessage(self, message):
        if message is None: return
        try:
            message['m']
        except KeyError:
            return None

        if message['m'] == 'qsd':
            self.forTicker(message)

    # parse ticker data
    def forTicker(self, receiveddata):
        symbol = receiveddata['p'][1]['n']
        data = receiveddata['p'][1]['v']
        try:
            self.states[symbol]['volume'] = data['volume']
        except KeyError:
            self.states[symbol]['volume'] += 0
        try:
            self.states[symbol]['price'] = data['lp']
        except KeyError:
            self.states[symbol]['price'] += 0
        try:
            self.states[symbol]['changePercentage'] = data['chp']
        except KeyError:
            self.states[symbol]['changePercentage'] += 0
        try:
            self.states[symbol]['change'] = data['ch']
        except KeyError:
             self.states[symbol]['change'] += 0
        self.insertData(self.states[symbol]['volume'], self.states[symbol]['price'], symbol)
        if self.verbose:
            self.saves += 1

    # send status messages every 5 seconds if enabled
    async def giveAnUpdate(self):
        while True:
            await asyncio.sleep(5)
            print("{}: Watching {} tickers → received {} updates".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), len(self.symbols), self.saves))
            self.saves = 0

    # start ticker in new thread
    def start(self):
        self.loop = asyncio.new_event_loop()
        def _start(loop):
            asyncio.set_event_loop(loop)
            self.task = loop.create_task(self.connect())
            if self.verbose:
                self.updateTask = loop.create_task(self.giveAnUpdate())
            loop.run_forever()

        t = threading.Thread(target=_start, args=(self.loop,))
        t.start()
        self.thread = t

    # stop it :(
    def stop(self):
        self.task.cancel()
        if self.verbose:
            self.updateTask.cancel()
        self.loop.stop()
        self.thread.join()
        self.db.close()