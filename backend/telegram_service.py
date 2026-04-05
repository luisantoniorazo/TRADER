import logging
import httpx
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class TelegramNotificationService:
    """Sends notifications via Telegram Bot API using httpx (no external lib needed)."""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def send_message(self, text: str) -> bool:
        if not self.enabled:
            logger.warning("Telegram not configured, skipping message")
            return False

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"},
                )
                data = resp.json()
                if data.get("ok"):
                    logger.info("Telegram message sent OK")
                    return True

                logger.warning(f"Telegram HTML failed: {data.get('description')}")
                # Retry as plain text if HTML parse fails
                resp2 = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={"chat_id": self.chat_id, "text": text},
                )
                data2 = resp2.json()
                if data2.get("ok"):
                    logger.info("Telegram message sent OK (plain text fallback)")
                    return True
                logger.error(f"Telegram send failed: {data2}")
                return False
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False

    async def send_trade_notification(self, trade: dict):
        side = trade.get("side", "?")
        symbol = trade.get("symbol", "?")
        qty = trade.get("quantity", 0)

        if side == "BUY":
            entry_price = trade.get("entry_price", 0)
            total_cost = entry_price * qty
            msg = (
                f"🟢 <b>COMPRA Ejecutada</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Simbolo: {symbol}\n"
                f"Precio: ${entry_price:.4f}\n"
                f"Cantidad: {qty:.6f}\n"
                f"Inversion: ${total_cost:.2f} USDT\n\n"
                f"Estado: Posicion ABIERTA\n"
                f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )
        else:
            entry_price = trade.get("entry_price", 0)
            exit_price = trade.get("exit_price", 0)
            pl = trade.get("profit_loss", 0)
            pl_pct = ((exit_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
            total_invertido = entry_price * qty
            total_retirado = exit_price * qty
            icon = "💰" if pl > 0 else "📉"
            result = "GANANCIA" if pl > 0 else "PERDIDA"
            msg = (
                f"🔴 <b>VENTA Ejecutada</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Simbolo: {symbol}\n"
                f"Precio Entrada: ${entry_price:.4f}\n"
                f"Precio Salida: ${exit_price:.4f}\n"
                f"Cantidad: {qty:.6f}\n\n"
                f"💵 Invertido: ${total_invertido:.2f} USDT\n"
                f"💵 Retirado: ${total_retirado:.2f} USDT\n\n"
                f"{icon} <b>Resultado: {result}</b>\n"
                f"P&L: ${pl:+.2f} ({pl_pct:+.2f}%)\n\n"
                f"Estado: Posicion CERRADA\n"
                f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )

        await self.send_message(msg)

    async def send_daily_report(self, stats: dict, balance: float):
        total_profit = stats.get("total_profit", 0)
        icon = "📈" if total_profit > 0 else "📉"

        msg = (
            f"📊 <b>Reporte Diario de Trading</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{icon} Ganancia del Dia: ${total_profit:.2f}\n"
            f"💰 Saldo Actual: ${balance:.2f}\n\n"
            f"<b>Estadisticas:</b>\n"
            f"  Trades Totales: {stats.get('total_trades', 0)}\n"
            f"  Trades Ganadores: {stats.get('winning_trades', 0)}\n"
            f"  Trades Perdedores: {stats.get('losing_trades', 0)}\n"
            f"  Win Rate: {stats.get('win_rate', 0):.1f}%\n\n"
            f"<b>Progreso hacia Meta:</b>\n"
            f"  Meta Diaria: $1,000\n"
            f"  Progreso: {stats.get('progress', 0):.1f}%\n\n"
            f"🤖 <i>AlgoTrade X - Trading Automatizado</i>\n"
            f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        await self.send_message(msg)

    async def send_bot_status_notification(self, is_running: bool, strategy: str = None):
        if is_running:
            msg = (
                f"🚀 <b>Bot de Trading Iniciado</b>\n\n"
                f"Estado: Activo ✅\n"
                f"Estrategia: {strategy or 'Scalping Agresivo'}\n\n"
                f"🔄 Reinversion Automatica: 5% del saldo por trade\n"
                f"💰 Crecimiento Compuesto activo\n\n"
                f"El bot esta monitoreando el mercado."
            )
        else:
            msg = (
                "⏸️ <b>Bot de Trading Detenido</b>\n\n"
                "Estado: Inactivo ❌\n\n"
                "El bot ha sido detenido."
            )
        await self.send_message(msg)

    async def send_error_notification(self, error_message: str):
        msg = (
            f"⚠️ <b>Error en el Bot</b>\n\n"
            f"{error_message}\n\n"
            f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        await self.send_message(msg)


# --------------- Global singleton ---------------
_telegram_service: TelegramNotificationService = None


def initialize_telegram_service(bot_token: str, chat_id: str):
    global _telegram_service
    _telegram_service = TelegramNotificationService(bot_token, chat_id)
    logger.info(f"Telegram service initialized (chat_id={chat_id})")
    return _telegram_service


def get_telegram_service():
    return _telegram_service
