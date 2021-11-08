import asyncio, websockets, random, json, threading

def createRandomToken(length=12):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for i in range(length))


class ticker:
    
    def __init__(self, symbol='BINANCE:BTCUSDT'):
        self.loop = asyncio.get_event_loop()
        self.symbol = symbol
        self.state = {'volume': 0, 'price': 0, 'change': 0, 'changePercentage': 0}

    # Connect to websocket
    async def connect(self):
        async with websockets.connect("wss://data.tradingview.com/socket.io/websocket", origin="https://www.tradingview.com") as connection: # ?from=chart%2F&date=2021_11_05-16_38
            self.connection = connection
            await self.waitForMessages()
            await asyncio.Future()

    # Loop waiting for messages
    async def waitForMessages(self):
        await self.authenticate()
        while True:
            message = await self.readMessage(await self.connection.recv())
            print(message)
            self.parseMessage(message)

    # Convert message string to object
    async def readMessage(self, message):
        try:
            return json.loads(message.split('~m~')[2])
        except Exception as err:
            if '~h~' in message:
                await self.connection.send(message)
            else:
                print(err)

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
        self.qs = 'qs_' + createRandomToken()
        self.cs = 'cs_' + createRandomToken()

        await self.sendMessage("set_auth_token", ["unauthorized_user_token"])
        await self.sendMessage("chart_create_session", [self.cs, ""])
        await self.sendMessage("quote_create_session", [self.qs])
        await self.sendMessage("quote_set_fields", [self.qs, "ch","chp","current_session","description","local_description","language","exchange","fractional","is_tradable","lp","lp_time","minmov","minmove2","original_name","pricescale","pro_name","short_name","type","update_mode","volume","currency_code","rchp","rtc"])
        await self.sendMessage("quote_add_symbols",[self.qs, self.symbol, {"flags":['force_permission']}])
        await self.sendMessage("quote_fast_symbols", [self.qs, self.symbol])
        return 0

    # this is so fricking messy
    def parseMessage(self, message):
        if message is None: return
        try:
            message['m']
        except KeyError:
            return None

        if message['m'] == 'qsd':
            self.forTicker(message['p'][1]['v'])

    # parse ticker data
    def forTicker(self, data):
        try:
            self.state['volume'] = data['volume']
        except KeyError:
            self.state['volume'] += 0
        try:
            self.state['price'] = data['lp']
        except KeyError:
            self.state['price'] += 0
        try:
            self.state['changePercentage'] = data['chp']
        except KeyError:
            self.state['changePercentage'] += 0
        try:
            self.state['change'] = data['ch']
        except KeyError:
             self.state['change'] += 0

    # start ticker in new thread
    def start(self):
        self.loop = asyncio.new_event_loop()
        def _start(loop):
            asyncio.set_event_loop(loop)
            self.task = loop.create_task(self.connect())
            loop.run_forever()

        t = threading.Thread(target=_start, args=(self.loop,))
        t.start()

    # stop it :(
    def stop(self):
        self.loop.stop()

tick = ticker()
tick.start()
