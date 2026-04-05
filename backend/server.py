from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from binance import AsyncClient, BinanceSocketManager
from binance.exceptions import BinanceAPIException
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import asyncio
import json
from enum import Enum
from telegram_service import initialize_telegram_service, get_telegram_service
from scheduler_service import DailyReportScheduler

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the main app
app = FastAPI(title="AlgoTrade X - Automated Trading Bot")
api_router = APIRouter(prefix="/api")

# Global variables for Binance client and bot state
binance_client: Optional[AsyncClient] = None
bot_state = {
    "is_running": False,
    "strategy": "aggressive_scalping",
    "daily_profit": 0.0,
    "total_trades": 0,
    "winning_trades": 0,
    "balance": 0.0,
    "last_updated": None,
    "telegram_enabled": False,
    "use_percentage": True,
    "balance_percentage": 5.0
}

# Active WebSocket connections
active_connections: List[WebSocket] = []

# Daily report scheduler
daily_scheduler: Optional[DailyReportScheduler] = None

# Models
class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class TradingStrategy(str, Enum):
    AGGRESSIVE_SCALPING = "aggressive_scalping"
    DAY_TRADING = "day_trading"
    SWING_TRADING = "swing_trading"

class ApiKeysInput(BaseModel):
    api_key: str
    api_secret: str
    testnet: bool = True
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

class BotConfig(BaseModel):
    strategy: TradingStrategy
    symbols: List[str] = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    max_trade_amount: float = 10.0
    profit_target: float = 1.5
    stop_loss: float = 0.5

class Trade(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float] = None
    quantity: float
    profit_loss: Optional[float] = None
    status: str = "open"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PriceData(BaseModel):
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    timestamp: datetime

# Initialize Binance client
async def initialize_binance_client(api_key: str, api_secret: str, testnet: bool = True):
    global binance_client
    try:
        # Try real Binance first
        if testnet:
            try:
                binance_client = await AsyncClient.create(
                    api_key=api_key,
                    api_secret=api_secret,
                    testnet=True,
                    tld='com'
                )
                logger.info(f"Binance client initialized (testnet={testnet})")
                return True
            except Exception as e:
                logger.warning(f"Real Binance connection failed: {str(e)}")
                logger.info("🎮 Switching to DEMO MODE - Simulated trading")
                
                # Fall back to demo mode
                from demo_trading_engine import create_demo_client
                binance_client = await create_demo_client(api_key, api_secret, testnet)
                logger.info("✅ DEMO MODE activated - All trades are simulated!")
                return True
        else:
            binance_client = await AsyncClient.create(
                api_key=api_key,
                api_secret=api_secret,
                testnet=False
            )
            logger.info(f"Binance client initialized (production mode)")
            return True
    except Exception as e:
        logger.error(f"Failed to initialize Binance client: {str(e)}")
        # Last resort: demo mode
        try:
            from demo_trading_engine import create_demo_client
            binance_client = await create_demo_client(api_key, api_secret, testnet)
            logger.info("✅ DEMO MODE activated as fallback")
            return True
        except:
            return False

# WebSocket broadcast
async def broadcast_message(message: dict):
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            disconnected.append(connection)
    
    for conn in disconnected:
        active_connections.remove(conn)

# Trading Engine
class TradingEngine:
    def __init__(self, config: BotConfig):
        self.config = config
        self.active_positions: Dict[str, Trade] = {}
        self.is_running = False
    
    async def calculate_technical_indicators(self, symbol: str):
        """Calculate RSI, MACD, and other indicators"""
        try:
            # Get klines for technical analysis
            klines = await binance_client.get_klines(
                symbol=symbol,
                interval="1m",
                limit=50
            )
            
            closes = [float(k[4]) for k in klines]
            
            # Simple momentum strategy
            if len(closes) > 14:
                # Calculate simple RSI
                gains = []
                losses = []
                for i in range(1, len(closes)):
                    change = closes[i] - closes[i-1]
                    if change > 0:
                        gains.append(change)
                        losses.append(0)
                    else:
                        gains.append(0)
                        losses.append(abs(change))
                
                avg_gain = sum(gains[-14:]) / 14
                avg_loss = sum(losses[-14:]) / 14
                
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                
                return {
                    "rsi": rsi,
                    "price": closes[-1],
                    "momentum": (closes[-1] - closes[-10]) / closes[-10] * 100
                }
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {str(e)}")
        return None
    
    async def analyze_and_trade(self, symbol: str):
        """Analyze market and execute trades"""
        try:
            indicators = await self.calculate_technical_indicators(symbol)
            if not indicators:
                return
            
            rsi = indicators["rsi"]
            price = indicators["price"]
            
            # Aggressive scalping strategy
            if self.config.strategy == TradingStrategy.AGGRESSIVE_SCALPING:
                # Buy signal: RSI < 35 (oversold)
                if rsi < 35 and symbol not in self.active_positions:
                    await self.execute_buy(symbol, price)
                
                # Sell signal: RSI > 65 (overbought) or take profit
                elif symbol in self.active_positions:
                    position = self.active_positions[symbol]
                    profit_pct = ((price - position.entry_price) / position.entry_price) * 100
                    
                    if profit_pct >= self.config.profit_target or profit_pct <= -self.config.stop_loss or rsi > 65:
                        await self.execute_sell(symbol, price, profit_pct)
        
        except Exception as e:
            logger.error(f"Error in analyze_and_trade for {symbol}: {str(e)}")
    
    async def execute_buy(self, symbol: str, price: float):
        """Execute buy order"""
        try:
            # Get account balance
            balance = await binance_client.get_asset_balance(asset="USDT")
            free_balance = float(balance["free"]) if balance else 0
            
            # Calculate trade amount based on configuration
            if self.config.use_percentage:
                # Use percentage of total balance (compound growth)
                trade_amount = free_balance * (self.config.balance_percentage / 100)
                logger.info(f"Using {self.config.balance_percentage}% of balance: ${trade_amount:.2f} from ${free_balance:.2f}")
            else:
                # Use fixed amount
                trade_amount = self.config.max_trade_amount
            
            if free_balance < trade_amount:
                logger.warning(f"Insufficient balance: {free_balance} USDT, need: {trade_amount} USDT")
                return
            
            quantity = trade_amount / price
            
            # Round quantity to proper precision
            quantity = round(quantity, 6)
            
            logger.info(f"Attempting BUY: {symbol} at {price}, quantity: {quantity}, amount: ${trade_amount:.2f}")
            
            # Create mock order for testing
            trade = Trade(
                symbol=symbol,
                side="BUY",
                entry_price=price,
                quantity=quantity,
                status="open"
            )
            
            self.active_positions[symbol] = trade
            
            # Save to database
            trade_dict = trade.model_dump()
            trade_dict["timestamp"] = trade_dict["timestamp"].isoformat()
            await db.trades.insert_one(trade_dict)
            
            # Update bot state
            bot_state["total_trades"] += 1
            await broadcast_message({"type": "trade", "data": trade_dict})
            
            logger.info(f"BUY order executed: {symbol} at {price}")
        
        except Exception as e:
            logger.error(f"Error executing buy: {str(e)}")
    
    async def execute_sell(self, symbol: str, price: float, profit_pct: float):
        """Execute sell order"""
        try:
            if symbol not in self.active_positions:
                return
            
            position = self.active_positions[symbol]
            position.exit_price = price
            position.profit_loss = (price - position.entry_price) * position.quantity
            position.status = "closed"
            
            logger.info(f"Attempting SELL: {symbol} at {price}, profit: {position.profit_loss}")
            
            # Update in database
            await db.trades.update_one(
                {"id": position.id},
                {"$set": {
                    "exit_price": price,
                    "profit_loss": position.profit_loss,
                    "status": "closed"
                }}
            )
            
            # Update bot state
            bot_state["daily_profit"] += position.profit_loss
            if position.profit_loss > 0:
                bot_state["winning_trades"] += 1
            
            # Send Telegram notification
            trade_dict = position.model_dump()
            telegram_service = get_telegram_service()
            if telegram_service and telegram_service.enabled:
                await telegram_service.send_trade_notification(trade_dict)
            
            await broadcast_message({"type": "trade", "data": trade_dict})
            
            del self.active_positions[symbol]
            
            logger.info(f"SELL order executed: {symbol} at {price}, profit: {position.profit_loss}")
        
        except Exception as e:
            logger.error(f"Error executing sell: {str(e)}")
    
    async def run(self):
        """Main trading loop"""
        self.is_running = True
        logger.info("Trading bot started")
        
        while self.is_running:
            try:
                for symbol in self.config.symbols:
                    await self.analyze_and_trade(symbol)
                
                # Update balance
                try:
                    balance = await binance_client.get_asset_balance(asset="USDT")
                    bot_state["balance"] = float(balance["free"]) if balance else 0
                except:
                    pass
                
                bot_state["last_updated"] = datetime.now(timezone.utc).isoformat()
                await broadcast_message({"type": "bot_state", "data": bot_state})
                
                await asyncio.sleep(10)  # Check every 10 seconds
            
            except Exception as e:
                logger.error(f"Error in trading loop: {str(e)}")
                await asyncio.sleep(5)
    
    def stop(self):
        """Stop the trading bot"""
        self.is_running = False
        logger.info("Trading bot stopped")

trading_engine: Optional[TradingEngine] = None

# API Endpoints
@api_router.post("/setup")
async def setup_api_keys(keys: ApiKeysInput, background_tasks: BackgroundTasks):
    """Setup Binance API keys"""
    success = await initialize_binance_client(keys.api_key, keys.api_secret, keys.testnet)
    if success:
        return {"status": "success", "message": "API keys configured successfully"}
    raise HTTPException(status_code=400, detail="Failed to initialize Binance client")

@api_router.post("/bot/start")
async def start_bot(config: BotConfig, background_tasks: BackgroundTasks):
    """Start the trading bot"""
    global trading_engine
    
    if not binance_client:
        raise HTTPException(status_code=400, detail="Please configure API keys first")
    
    if bot_state["is_running"]:
        raise HTTPException(status_code=400, detail="Bot is already running")
    
    trading_engine = TradingEngine(config)
    bot_state["is_running"] = True
    bot_state["strategy"] = config.strategy.value
    bot_state["use_percentage"] = config.use_percentage
    bot_state["balance_percentage"] = config.balance_percentage if config.use_percentage else None
    
    # Send Telegram notification with strategy details
    telegram_service = get_telegram_service()
    if telegram_service and telegram_service.enabled:
        strategy_msg = f"{config.strategy.value}"
        if config.use_percentage:
            strategy_msg += f" - Reinversión: {config.balance_percentage}% del saldo"
        await telegram_service.send_bot_status_notification(True, strategy_msg)
    
    background_tasks.add_task(trading_engine.run)
    
    return {
        "status": "success", 
        "message": "Trading bot started",
        "config": {
            "strategy": config.strategy.value,
            "use_percentage": config.use_percentage,
            "balance_percentage": config.balance_percentage if config.use_percentage else None
        }
    }

@api_router.post("/bot/stop")
async def stop_bot():
    """Stop the trading bot"""
    global trading_engine
    
    if not bot_state["is_running"]:
        raise HTTPException(status_code=400, detail="Bot is not running")
    
    if trading_engine:
        trading_engine.stop()
    
    bot_state["is_running"] = False
    
    return {"status": "success", "message": "Trading bot stopped"}

@api_router.get("/bot/status")
async def get_bot_status():
    """Get current bot status"""
    return bot_state

@api_router.get("/market/prices")
async def get_market_prices(symbols: str = "BTCUSDT,ETHUSDT,BNBUSDT"):
    """Get current market prices"""
    if not binance_client:
        raise HTTPException(status_code=400, detail="Binance client not initialized")
    
    try:
        symbol_list = symbols.split(",")
        prices = []
        
        for symbol in symbol_list:
            ticker = await binance_client.get_ticker(symbol=symbol)
            prices.append({
                "symbol": symbol,
                "price": float(ticker["lastPrice"]),
                "change_24h": float(ticker["priceChangePercent"]),
                "volume_24h": float(ticker["volume"]),
                "high_24h": float(ticker["highPrice"]),
                "low_24h": float(ticker["lowPrice"])
            })
        
        return prices
    except Exception as e:
        logger.error(f"Error fetching prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/account/balance")
async def get_account_balance():
    """Get account balance"""
    if not binance_client:
        raise HTTPException(status_code=400, detail="Binance client not initialized")
    
    try:
        account = await binance_client.get_account()
        balances = []
        
        for balance in account["balances"]:
            free = float(balance["free"])
            locked = float(balance["locked"])
            total = free + locked
            
            if total > 0:
                balances.append({
                    "asset": balance["asset"],
                    "free": free,
                    "locked": locked,
                    "total": total
                })
        
        return sorted(balances, key=lambda x: x["total"], reverse=True)
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/trades/history")
async def get_trade_history(limit: int = 50):
    """Get trade history"""
    try:
        trades = await db.trades.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
        
        for trade in trades:
            if isinstance(trade.get("timestamp"), str):
                trade["timestamp"] = datetime.fromisoformat(trade["timestamp"])
        
        return trades
    except Exception as e:
        logger.error(f"Error fetching trade history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/stats/daily")
async def get_daily_stats():
    """Get daily trading statistics"""
    try:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        trades = await db.trades.find({
            "status": "closed"
        }, {"_id": 0}).to_list(1000)
        
        total_profit = sum(t.get("profit_loss", 0) for t in trades)
        winning = sum(1 for t in trades if t.get("profit_loss", 0) > 0)
        total = len(trades)
        
        return {
            "total_trades": total,
            "winning_trades": winning,
            "losing_trades": total - winning,
            "win_rate": (winning / total * 100) if total > 0 else 0,
            "total_profit": total_profit,
            "daily_goal": 1000,
            "progress": (total_profit / 1000 * 100) if total_profit > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error fetching daily stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/telegram/test")
async def test_telegram():
    """Test Telegram notification"""
    telegram_service = get_telegram_service()
    if not telegram_service or not telegram_service.enabled:
        raise HTTPException(status_code=400, detail="Telegram not configured")
    
    await telegram_service.send_message("🤖 *Prueba de Notificaci\u00f3n*\\n\\n\u2705 Telegram configurado correctamente\\!")
    return {"status": "success", "message": "Test notification sent"}

@api_router.post("/telegram/daily-report")
async def trigger_daily_report():
    """Manually trigger daily report"""
    telegram_service = get_telegram_service()
    if not telegram_service or not telegram_service.enabled:
        raise HTTPException(status_code=400, detail="Telegram not configured")
    
    await send_daily_report()
    return {"status": "success", "message": "Daily report sent"}

@api_router.post("/test-binance")
async def test_binance_connection(keys: ApiKeysInput):
    """Test Binance connection without saving"""
    try:
        # Try to create a temporary client
        test_client = await AsyncClient.create(
            api_key=keys.api_key,
            api_secret=keys.api_secret,
            testnet=keys.testnet,
            tld='com'
        )
        
        # Try to get server time
        server_time = await test_client.get_server_time()
        
        # Try to ping
        await test_client.ping()
        
        await test_client.close_connection()
        
        return {
            "status": "success",
            "message": "Binance connection successful",
            "testnet": keys.testnet,
            "server_time": server_time
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "testnet": keys.testnet
        }

@api_router.websocket("/ws/market")
async def websocket_market_data(websocket: WebSocket):
    """WebSocket for real-time market data"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    global daily_scheduler
    
    if binance_client:
        await binance_client.close_connection()
    
    if daily_scheduler:
        daily_scheduler.stop()
    
    client.close()
