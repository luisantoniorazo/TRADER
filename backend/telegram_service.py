import asyncio
import logging
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime, timezone
import os

logger = logging.getLogger(__name__)

class TelegramNotificationService:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
    
    async def send_message(self, message: str):
        """Send a message to Telegram"""
        if not self.enabled:
            logger.warning("Telegram not configured, message not sent")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info("Telegram message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False
    
    async def send_trade_notification(self, trade: dict):
        """Send notification when a trade is executed"""
        side_emoji = "🟢" if trade["side"] == "BUY" else "🔴"
        
        message = f"""
{side_emoji} *Trade Ejecutado*

*Símbolo:* {trade['symbol']}
*Tipo:* {trade['side']}
*Precio:* ${trade.get('entry_price', trade.get('exit_price', 0)):.2f}
*Cantidad:* {trade.get('quantity', 0):.6f}

"""
        
        if trade.get('profit_loss') is not None:
            profit_emoji = "💰" if trade['profit_loss'] > 0 else "📉"
            message += f"{profit_emoji} *Ganancia/Pérdida:* ${trade['profit_loss']:.2f}\n"
        
        message += f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        await self.send_message(message)
    
    async def send_daily_report(self, stats: dict, balance: float):
        """Send daily trading report"""
        total_profit = stats.get('total_profit', 0)
        profit_emoji = "📈" if total_profit > 0 else "📉"
        
        message = f"""
📊 *Reporte Diario de Trading*
━━━━━━━━━━━━━━━━━━━━

{profit_emoji} *Ganancia del Día:* ${total_profit:.2f}
💰 *Saldo Actual:* ${balance:.2f}

*Estadísticas:*
• Trades Totales: {stats.get('total_trades', 0)}
• Trades Ganadores: {stats.get('winning_trades', 0)}
• Trades Perdedores: {stats.get('losing_trades', 0)}
• Win Rate: {stats.get('win_rate', 0):.1f}%

*Progreso hacia Meta:*
• Meta Diaria: $1,000
• Progreso: {stats.get('progress', 0):.1f}%

🤖 _AlgoTrade X - Trading Automatizado_
⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        
        await self.send_message(message)
    
    async def send_bot_status_notification(self, is_running: bool, strategy: str = None):
        """Send notification when bot starts or stops"""
        if is_running:
            message = f"""
🚀 *Bot de Trading Iniciado*

*Estado:* Activo ✅
*Estrategia:* {strategy or 'Scalping Agresivo'}

🔄 *Reinversión Automática:* 5% del saldo por trade
💰 *Crecimiento Compuesto:* Las ganancias se reinvierten automáticamente

_El bot está monitoreando el mercado y ejecutará trades automáticamente._
"""
        else:
            message = f"""
⏸️ *Bot de Trading Detenido*

*Estado:* Inactivo ❌

_El bot ha sido detenido y no ejecutará más trades._
"""
        
        await self.send_message(message)
    
    async def send_error_notification(self, error_message: str):
        """Send error notification"""
        message = f"""
⚠️ *Error en el Bot*

{error_message}

⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        await self.send_message(message)

# Global instance
telegram_service: TelegramNotificationService = None

def initialize_telegram_service(bot_token: str, chat_id: str):
    """Initialize the global Telegram service"""
    global telegram_service
    telegram_service = TelegramNotificationService(bot_token, chat_id)
    logger.info("Telegram notification service initialized")
    return telegram_service

def get_telegram_service():
    """Get the global Telegram service instance"""
    return telegram_service
