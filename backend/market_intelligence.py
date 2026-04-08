import logging
import httpx
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class MarketIntelligence:
    """Aggregates external signals: Fear & Greed, advanced indicators, BTC correlation."""

    def __init__(self):
        self.fear_greed_value = 50  # 0=Extreme Fear, 100=Extreme Greed
        self.fear_greed_label = "Neutral"
        self.btc_trend = "neutral"  # bullish / bearish / neutral
        self.btc_change_1h = 0.0
        self.last_update = None

    async def fetch_fear_greed(self):
        """Fetch Fear & Greed Index from Alternative.me API"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get("https://api.alternative.me/fng/?limit=1")
                data = resp.json()
                if data.get("data"):
                    entry = data["data"][0]
                    self.fear_greed_value = int(entry["value"])
                    self.fear_greed_label = entry["value_classification"]
                    logger.info(f"Fear & Greed: {self.fear_greed_value} ({self.fear_greed_label})")
        except Exception as e:
            logger.warning(f"Failed to fetch Fear & Greed: {e}")

    async def analyze_btc_trend(self, binance_client):
        """Analyze BTC trend using price data from Binance"""
        try:
            klines = await binance_client.get_klines(
                symbol="BTCUSDT", interval="1h", limit=26
            )
            closes = [float(k[4]) for k in klines]

            if len(closes) < 2:
                return

            current = closes[-1]
            prev_1h = closes[-2]
            self.btc_change_1h = ((current - prev_1h) / prev_1h) * 100

            # Simple trend from last 6 hours
            avg_recent = sum(closes[-3:]) / 3
            avg_older = sum(closes[-6:-3]) / 3

            if avg_recent > avg_older * 1.002:
                self.btc_trend = "bullish"
            elif avg_recent < avg_older * 0.998:
                self.btc_trend = "bearish"
            else:
                self.btc_trend = "neutral"

            logger.info(f"BTC trend: {self.btc_trend} (1h change: {self.btc_change_1h:+.2f}%)")
        except Exception as e:
            logger.warning(f"Failed to analyze BTC trend: {e}")

    def calculate_macd(self, closes: list) -> dict:
        """Calculate MACD (12, 26, 9) from close prices"""
        if len(closes) < 26:
            return {"macd": 0, "signal": 0, "histogram": 0, "trend": "neutral"}

        ema12 = self._ema(closes, 12)
        ema26 = self._ema(closes, 26)
        macd_line = ema12 - ema26

        # Build MACD series for signal line
        macd_series = []
        for i in range(26, len(closes) + 1):
            e12 = self._ema(closes[:i], 12)
            e26 = self._ema(closes[:i], 26)
            macd_series.append(e12 - e26)

        signal_line = self._ema(macd_series, 9) if len(macd_series) >= 9 else macd_line
        histogram = macd_line - signal_line

        if histogram > 0 and macd_line > 0:
            trend = "bullish"
        elif histogram < 0 and macd_line < 0:
            trend = "bearish"
        else:
            trend = "neutral"

        return {"macd": macd_line, "signal": signal_line, "histogram": histogram, "trend": trend}

    def calculate_bollinger(self, closes: list, period: int = 20, std_dev: float = 2.0) -> dict:
        """Calculate Bollinger Bands"""
        if len(closes) < period:
            return {"upper": 0, "middle": 0, "lower": 0, "position": "middle"}

        window = closes[-period:]
        middle = sum(window) / period
        variance = sum((x - middle) ** 2 for x in window) / period
        std = variance ** 0.5

        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        current = closes[-1]

        if current <= lower:
            position = "below_lower"  # Oversold - buy signal
        elif current >= upper:
            position = "above_upper"  # Overbought - sell signal
        elif current < middle:
            position = "lower_half"
        else:
            position = "upper_half"

        return {"upper": upper, "middle": middle, "lower": lower, "position": position}

    def calculate_ma200(self, closes: list) -> dict:
        """Calculate 200-period Moving Average"""
        if len(closes) < 200:
            # Use whatever we have
            period = min(len(closes), 50)
            if period < 10:
                return {"ma": 0, "above": True, "distance_pct": 0}
            ma = sum(closes[-period:]) / period
        else:
            ma = sum(closes[-200:]) / 200

        current = closes[-1]
        above = current > ma
        distance_pct = ((current - ma) / ma) * 100 if ma > 0 else 0

        return {"ma": ma, "above": above, "distance_pct": distance_pct}

    async def get_advanced_indicators(self, binance_client, symbol: str) -> dict:
        """Get MACD, Bollinger, MA200 for a symbol"""
        try:
            klines = await binance_client.get_klines(
                symbol=symbol, interval="5m", limit=200
            )
            closes = [float(k[4]) for k in klines]

            macd = self.calculate_macd(closes)
            bollinger = self.calculate_bollinger(closes)
            ma200 = self.calculate_ma200(closes)

            return {
                "macd": macd,
                "bollinger": bollinger,
                "ma200": ma200
            }
        except Exception as e:
            logger.debug(f"Failed to get indicators for {symbol}: {e}")
            return {
                "macd": {"macd": 0, "signal": 0, "histogram": 0, "trend": "neutral"},
                "bollinger": {"upper": 0, "middle": 0, "lower": 0, "position": "middle"},
                "ma200": {"ma": 0, "above": True, "distance_pct": 0}
            }

    def should_buy(self, rsi: float, indicators: dict, strategy_rsi_threshold: float) -> tuple:
        """
        Smart buy decision combining all signals.
        Returns (should_buy: bool, confidence: str, reason: str)
        """
        score = 0
        reasons = []

        # RSI signal (base)
        if rsi < strategy_rsi_threshold:
            score += 2
            reasons.append(f"RSI={rsi:.0f} sobrevendido")

        # Fear & Greed - buy when fearful
        if self.fear_greed_value < 25:
            score += 2
            reasons.append(f"Miedo extremo ({self.fear_greed_value})")
        elif self.fear_greed_value < 40:
            score += 1
            reasons.append(f"Mercado con miedo ({self.fear_greed_value})")
        elif self.fear_greed_value > 75:
            score -= 2
            reasons.append(f"Codicia extrema ({self.fear_greed_value}) - riesgoso")

        # BTC correlation - don't buy altcoins if BTC is crashing
        if self.btc_trend == "bearish" and self.btc_change_1h < -1.0:
            score -= 2
            reasons.append(f"BTC cayendo {self.btc_change_1h:.1f}%")
        elif self.btc_trend == "bullish":
            score += 1
            reasons.append("BTC alcista")

        # MACD
        macd = indicators.get("macd", {})
        if macd.get("trend") == "bullish" and macd.get("histogram", 0) > 0:
            score += 1
            reasons.append("MACD alcista")
        elif macd.get("trend") == "bearish":
            score -= 1
            reasons.append("MACD bajista")

        # Bollinger
        bollinger = indicators.get("bollinger", {})
        if bollinger.get("position") == "below_lower":
            score += 2
            reasons.append("Precio bajo Bollinger inferior")
        elif bollinger.get("position") == "above_upper":
            score -= 1
            reasons.append("Precio sobre Bollinger superior")

        # MA200
        ma200 = indicators.get("ma200", {})
        if ma200.get("above"):
            score += 1
            reasons.append("Sobre MA200")

        # Decision
        if score >= 3:
            confidence = "alta"
        elif score >= 1:
            confidence = "media"
        else:
            confidence = "baja"

        should = score >= 2 and rsi < strategy_rsi_threshold
        reason = " | ".join(reasons) if reasons else "Sin senales claras"

        return should, confidence, reason

    def should_sell(self, rsi: float, profit_pct: float, indicators: dict, strategy_rsi_threshold: float, profit_target: float, stop_loss: float) -> tuple:
        """
        Smart sell decision combining all signals.
        Returns (should_sell: bool, reason: str)
        """
        # Always honor stop loss
        if profit_pct <= -stop_loss:
            return True, f"Stop loss: {profit_pct:.2f}%"

        # Always honor profit target
        if profit_pct >= profit_target:
            return True, f"Target alcanzado: {profit_pct:.2f}%"

        reasons = []

        # RSI overbought
        if rsi > strategy_rsi_threshold:
            reasons.append(f"RSI={rsi:.0f} sobrecomprado")

        # Fear & Greed extreme greed - take profits
        if self.fear_greed_value > 80 and profit_pct > 0:
            reasons.append(f"Codicia extrema ({self.fear_greed_value})")

        # BTC crashing - protect capital
        if self.btc_trend == "bearish" and self.btc_change_1h < -2.0:
            reasons.append(f"BTC desplome {self.btc_change_1h:.1f}%")

        # MACD bearish crossover
        macd = indicators.get("macd", {})
        if macd.get("trend") == "bearish" and macd.get("histogram", 0) < 0:
            reasons.append("MACD bajista")

        # Bollinger upper band
        bollinger = indicators.get("bollinger", {})
        if bollinger.get("position") == "above_upper":
            reasons.append("Sobre Bollinger superior")

        should = len(reasons) >= 2
        reason = " | ".join(reasons) if reasons else "Manteniendo posicion"

        return should, reason

    async def refresh(self, binance_client):
        """Refresh all external data"""
        await self.fetch_fear_greed()
        if binance_client:
            await self.analyze_btc_trend(binance_client)
        self.last_update = datetime.now(timezone.utc).isoformat()

    def get_summary(self) -> dict:
        """Return current intelligence summary"""
        return {
            "fear_greed": {
                "value": self.fear_greed_value,
                "label": self.fear_greed_label
            },
            "btc_trend": {
                "trend": self.btc_trend,
                "change_1h": self.btc_change_1h
            },
            "last_update": self.last_update
        }

    def _ema(self, data: list, period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(data) < period:
            return sum(data) / len(data) if data else 0

        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period

        for price in data[period:]:
            ema = (price - ema) * multiplier + ema

        return ema
