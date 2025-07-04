class TradeExecutor:
    def __init__(self):
        self.mt5_connected = False
        self.supported_symbols = ['XAUUSDz', 'USTECz', 'US30z']
        self.symbol_info = {}
        
    def connect_mt5(self):
        try:
            if not mt5.initialize():
                raise ConnectionError("MT5 initialization failed")
                
            # Preload symbol info
            for symbol in self.supported_symbols:
                info = mt5.symbol_info(symbol)
                if info is None:
                    raise ValueError(f"Symbol {symbol} not available")
                self.symbol_info[symbol] = info
                
            self.mt5_connected = True
            return True
        except Exception as e:
            logging.error(f"MT5 connection error: {str(e)}")
            self.mt5_connected = False
            return False
    
    async def execute_trade(self, trade_data):
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                if not self.mt5_connected and not self.connect_mt5():
                    await asyncio.sleep(retry_delay)
                    continue
                    
                # Convert pips to price for the symbol
                symbol = trade_data['symbol']
                point = self.symbol_info[symbol].point
                digits = self.symbol_info[symbol].digits
                
                # Calculate prices based on pips
                if trade_data['action'].lower() == 'buy':
                    tp1 = trade_data['entry'] + 30 * point * 10
                    tp2 = trade_data['entry'] + 60 * point * 10
                    tp3 = trade_data['entry'] + 90 * point * 10
                else:  # sell
                    tp1 = trade_data['entry'] - 30 * point * 10
                    tp2 = trade_data['entry'] - 60 * point * 10
                    tp3 = trade_data['entry'] - 90 * point * 10
                
                request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": symbol,
                    "volume": trade_data['lot_size'],
                    "type": mt5.ORDER_TYPE_BUY_LIMIT if trade_data['action'].lower() == 'buy' 
                           else mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": round(trade_data['entry'], digits),
                    "sl": round(trade_data['sl'], digits),
                    "tp": round(tp3, digits),
                    "deviation": 10,
                    "magic": 2023,
                    "comment": "TG Signal",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                result = mt5.order_send(request)
                
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    error_msg = mt5.last_error()
                    if "not enough money" in error_msg.lower():
                        raise ValueError("Insufficient margin")
                    elif "slippage" in error_msg.lower():
                        await self.handle_slippage(request)
                        continue
                    raise RuntimeError(f"Trade failed: {error_msg}")
                
                # Start monitoring thread for this trade
                asyncio.create_task(self.monitor_trade(result.order, {
                    'entry': trade_data['entry'],
                    'tp1': tp1,
                    'tp2': tp2,
                    'tp3': tp3,
                    'sl': trade_data['sl']
                }))
                
                return True
                
            except Exception as e:
                logging.error(f"Trade attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    return False
                await asyncio.sleep(retry_delay)
    
    async def handle_slippage(self, request):
        """Adjust price to handle slippage"""
        new_price = mt5.symbol_info_tick(request['symbol']).ask if request['type'] == mt5.ORDER_TYPE_BUY_LIMIT \
                  else mt5.symbol_info_tick(request['symbol']).bid
        request['price'] = new_price
        request['action'] = mt5.TRADE_ACTION_DEAL  # Change to market order
        logging.warning(f"Adjusting to market order due to slippage at {new_price}")