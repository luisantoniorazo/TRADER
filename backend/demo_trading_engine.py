import asyncio
import random
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class DemoMarketData:
    """Simulate realistic crypto price movements"""
    
    def __init__(self):
        # Initialize with realistic prices for all 30 cryptos
        self.prices = {
            "BTCUSDT": 43000.0,
            "ETHUSDT": 2400.0,
            "BNBUSDT": 310.0,
            "SOLUSDT": 98.0,
            "XRPUSDT": 0.58,
            "ADAUSDT": 0.52,
            "DOGEUSDT": 0.082,
            "MATICUSDT": 0.89,
            "DOTUSDT": 7.2,
            "AVAXUSDT": 36.5,
            "SHIBUSDT": 0.000009,
            "LINKUSDT": 14.8,
            "ATOMUSDT": 9.8,
            "LTCUSDT": 72.0,
            "UNIUSDT": 6.2,
            "ETCUSDT": 20.5,
            "NEARUSDT": 2.1,
            "APTUSDT": 6.8,
            "ARBUSDT": 1.2,
            "OPUSDT": 2.4,
            "FILUSDT": 4.5,
            "LDOUSDT": 2.1,
            "INJUSDT": 22.0,
            "SUIUSDT": 0.78,
            "RNDRUSDT": 3.2,
            "PEPEUSDT": 0.0000012,
            "RUNEUSDT": 4.8,
            "AAVEUSDT": 95.0,
            "MKRUSDT": 1580.0,
            "SANDUSDT": 0.48,
            "MANAUSDT": 0.52,
            "GRTUSDT": 0.16,
            "ALGOUSDT": 0.19
        }
        self.volatility = {
            "BTCUSDT": 0.015,
            "ETHUSDT": 0.020,
            "BNBUSDT": 0.025,
            "SOLUSDT": 0.035,
            "XRPUSDT": 0.030,
            "ADAUSDT": 0.028,
            "DOGEUSDT": 0.045,
            "MATICUSDT": 0.032,
            "DOTUSDT": 0.030,
            "AVAXUSDT": 0.035,
            "SHIBUSDT": 0.050,
            "LINKUSDT": 0.028,
            "ATOMUSDT": 0.030,
            "LTCUSDT": 0.022,
            "UNIUSDT": 0.032,
            "ETCUSDT": 0.028,
            "NEARUSDT": 0.038,
            "APTUSDT": 0.040,
            "ARBUSDT": 0.035,
            "OPUSDT": 0.035,
            "FILUSDT": 0.030,
            "LDOUSDT": 0.035,
            "INJUSDT": 0.038,
            "SUIUSDT": 0.042,
            "RNDRUSDT": 0.040,
            "PEPEUSDT": 0.055,
            "RUNEUSDT": 0.035,
            "AAVEUSDT": 0.030,
            "MKRUSDT": 0.028,
            "SANDUSDT": 0.042,
            "MANAUSDT": 0.040,
            "GRTUSDT": 0.035,
            "ALGOUSDT": 0.032
        }
    
    def get_price(self, symbol: str) -> float:
        """Get current simulated price"""
        if symbol not in self.prices:
            # Return a default price for unknown symbols
            logger.warning(f"Unknown symbol {symbol}, returning default price")
            return 1.0
        
        # Simulate price movement
        current_price = self.prices[symbol]
        volatility = self.volatility.get(symbol, 0.025)
        
        # Random walk with drift
        change_pct = random.gauss(0, volatility)
        new_price = current_price * (1 + change_pct)
        
        # Ensure price doesn't go negative or too extreme
        if new_price < current_price * 0.8:
            new_price = current_price * 0.8
        elif new_price > current_price * 1.2:
            new_price = current_price * 1.2
        
        self.prices[symbol] = new_price
        return new_price
    
    def get_ticker(self, symbol: str) -> dict:
        """Get ticker data like Binance API"""
        price = self.get_price(symbol)
        change_24h = random.uniform(-5.0, 5.0)
        
        return {
            "symbol": symbol,
            "lastPrice": str(price),
            "priceChangePercent": str(change_24h),
            "volume": str(random.uniform(10000, 50000)),
            "highPrice": str(price * 1.03),
            "lowPrice": str(price * 0.97)
        }
    
    def get_klines(self, symbol: str, interval: str, limit: int) -> list:
        """Simulate kline/candlestick data"""
        klines = []
        base_price = self.prices[symbol]
        
        for i in range(limit):
            open_price = base_price * (1 + random.gauss(0, 0.01))
            close_price = open_price * (1 + random.gauss(0, 0.01))
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.005))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.005))
            
            klines.append([
                int(datetime.now(timezone.utc).timestamp() * 1000) - (i * 60000),
                str(open_price),
                str(high_price),
                str(low_price),
                str(close_price),
                str(random.uniform(10, 100)),  # volume
                0,
                str(random.uniform(100000, 500000)),  # quote volume
                0, 0, 0, 0
            ])
        
        return list(reversed(klines))

class DemoAccount:
    """Simulate a Binance account"""
    
    def __init__(self, initial_balance=200.0):
        self.balances = {
            "USDT": {"free": initial_balance, "locked": 0.0},
            "BTC": {"free": 0.0, "locked": 0.0},
            "ETH": {"free": 0.0, "locked": 0.0},
            "BNB": {"free": 0.0, "locked": 0.0}
        }
    
    def get_balance(self, asset: str) -> dict:
        """Get balance for specific asset"""
        if asset not in self.balances:
            return {"free": "0", "locked": "0"}
        
        bal = self.balances[asset]
        return {
            "asset": asset,
            "free": str(bal["free"]),
            "locked": str(bal["locked"])
        }
    
    def get_account(self) -> dict:
        """Get full account information"""
        balances = []
        for asset, bal in self.balances.items():
            balances.append({
                "asset": asset,
                "free": str(bal["free"]),
                "locked": str(bal["locked"])
            })
        
        return {
            "makerCommission": 10,
            "takerCommission": 10,
            "buyerCommission": 0,
            "sellerCommission": 0,
            "canTrade": True,
            "canWithdraw": False,
            "canDeposit": False,
            "updateTime": int(datetime.now(timezone.utc).timestamp() * 1000),
            "balances": balances
        }
    
    def execute_trade(self, symbol: str, side: str, quantity: float, price: float) -> dict:
        """Simulate trade execution"""
        # Extract base and quote assets
        if "USDT" in symbol:
            quote_asset = "USDT"
            base_asset = symbol.replace("USDT", "")
        else:
            return {"error": "Unsupported symbol"}
        
        # Ensure assets exist
        if base_asset not in self.balances:
            self.balances[base_asset] = {"free": 0.0, "locked": 0.0}
        
        if side == "BUY":
            cost = quantity * price
            if self.balances[quote_asset]["free"] >= cost:
                self.balances[quote_asset]["free"] -= cost
                self.balances[base_asset]["free"] += quantity
                status = "FILLED"
                logger.info(f"✅ DEMO BUY executed: {symbol} - Cost: ${cost:.2f}, New USDT balance: ${self.balances[quote_asset]['free']:.2f}")
            else:
                status = "REJECTED"
                logger.warning(f"❌ DEMO BUY rejected: Insufficient balance")
        elif side == "SELL":
            if self.balances[base_asset]["free"] >= quantity:
                self.balances[base_asset]["free"] -= quantity
                proceeds = quantity * price
                self.balances[quote_asset]["free"] += proceeds
                status = "FILLED"
                logger.info(f"✅ DEMO SELL executed: {symbol} - Proceeds: ${proceeds:.2f}, New USDT balance: ${self.balances[quote_asset]['free']:.2f}")
            else:
                status = "REJECTED"
                logger.warning(f"❌ DEMO SELL rejected: Insufficient {base_asset}")
        
        return {
            "orderId": random.randint(10000000, 99999999),
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "status": status,
            "origQty": str(quantity),
            "executedQty": str(quantity) if status == "FILLED" else "0",
            "price": str(price),
            "transactTime": int(datetime.now(timezone.utc).timestamp() * 1000),
            "cummulativeQuoteQty": str(quantity * price)
        }

class DemoBinanceClient:
    """Demo client that mimics Binance AsyncClient API"""
    
    def __init__(self, api_key=None, api_secret=None):
        self.market_data = DemoMarketData()
        self.account = DemoAccount(initial_balance=200.0)
        logger.info("🎮 DEMO MODE: Binance client initialized with simulated trading")
    
    async def close_connection(self):
        """Mock close connection"""
        pass
    
    async def get_asset_balance(self, asset: str) -> dict:
        """Get balance for specific asset"""
        return self.account.get_balance(asset)
    
    async def get_account(self) -> dict:
        """Get full account information"""
        return self.account.get_account()
    
    async def get_ticker(self, symbol: str) -> dict:
        """Get ticker data"""
        return self.market_data.get_ticker(symbol)
    
    async def get_klines(self, symbol: str, interval: str, limit: int) -> list:
        """Get kline data"""
        return self.market_data.get_klines(symbol, interval, limit)
    
    async def get_avg_price(self, symbol: str) -> dict:
        """Get average price"""
        price = self.market_data.get_price(symbol)
        return {"price": str(price), "mins": 5}
    
    async def get_symbol_info(self, symbol: str) -> dict:
        """Get symbol information"""
        return {"symbol": symbol, "status": "TRADING"}
    
    async def get_exchange_info(self, symbol: str = None) -> dict:
        """Get exchange information"""
        symbols = [
            {"symbol": "BTCUSDT", "status": "TRADING"},
            {"symbol": "ETHUSDT", "status": "TRADING"},
            {"symbol": "BNBUSDT", "status": "TRADING"}
        ]
        
        if symbol:
            return {"symbols": [s for s in symbols if s["symbol"] == symbol]}
        
        return {"symbols": symbols}
    
    async def create_order(self, **params) -> dict:
        """Create an order"""
        symbol = params.get("symbol")
        side = params.get("side")
        quantity = float(params.get("quantity", 0))
        price = float(params.get("price", 0))
        
        if not price:
            # Market order - get current price
            price = self.market_data.get_price(symbol)
        
        result = self.account.execute_trade(symbol, side, quantity, price)
        logger.info(f"💰 Balance after trade - USDT: ${float(self.account.get_balance('USDT')['free']):.2f}")
        return result
    
    async def order_market(self, **params) -> dict:
        """Create market order"""
        return await self.create_order(**params)
    
    async def order_limit(self, **params) -> dict:
        """Create limit order"""
        return await self.create_order(**params)
    
    async def ping(self) -> dict:
        """Ping the server"""
        return {}
    
    async def get_server_time(self) -> dict:
        """Get server time"""
        return {"serverTime": int(datetime.now(timezone.utc).timestamp() * 1000)}

async def create_demo_client(api_key: str = None, api_secret: str = None, testnet: bool = True, db_client = None):
    """Create a demo Binance client - simplified version"""
    logger.info("🎮 Creating DEMO Binance client - No real trading!")
    client = DemoBinanceClient(api_key=api_key, api_secret=api_secret)
    return client
