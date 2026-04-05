import { useEffect, useState, useRef } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { Toaster } from "@/components/ui/sonner";
import PriceChart from "./PriceChart";
import TradesTable from "./TradesTable";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [isTestnet, setIsTestnet] = useState(true);
  const [telegramToken, setTelegramToken] = useState("");
  const [telegramChatId, setTelegramChatId] = useState("");
  const [isConfigured, setIsConfigured] = useState(false);
  const [botStatus, setBotStatus] = useState(null);
  const [prices, setPrices] = useState([]);
  const [balance, setBalance] = useState([]);
  const [trades, setTrades] = useState([]);
  const [dailyStats, setDailyStats] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    fetchBotStatus();
    const interval = setInterval(() => {
      if (isConfigured) {
        fetchPrices();
        fetchBalance();
        fetchTrades();
        fetchDailyStats();
        fetchBotStatus();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [isConfigured]);

  const fetchBotStatus = async () => {
    try {
      const response = await axios.get(`${API}/bot/status`);
      setBotStatus(response.data);
    } catch (error) {
      console.error("Error fetching bot status:", error);
    }
  };

  const fetchPrices = async () => {
    try {
      const response = await axios.get(`${API}/market/prices`);
      setPrices(response.data);
    } catch (error) {
      console.error("Error fetching prices:", error);
    }
  };

  const fetchBalance = async () => {
    try {
      const response = await axios.get(`${API}/account/balance`);
      setBalance(response.data);
    } catch (error) {
      console.error("Error fetching balance:", error);
    }
  };

  const fetchTrades = async () => {
    try {
      const response = await axios.get(`${API}/trades/history?limit=20`);
      setTrades(response.data);
    } catch (error) {
      console.error("Error fetching trades:", error);
    }
  };

  const fetchDailyStats = async () => {
    try {
      const response = await axios.get(`${API}/stats/daily`);
      setDailyStats(response.data);
    } catch (error) {
      console.error("Error fetching daily stats:", error);
    }
  };

  const handleSetupKeys = async () => {
    if (!apiKey || !apiSecret) {
      toast.error("Por favor ingresa tu API Key y Secret");
      return;
    }

    try {
      const payload = {
        api_key: apiKey,
        api_secret: apiSecret,
        testnet: isTestnet
      };
      
      if (telegramToken && telegramChatId) {
        payload.telegram_bot_token = telegramToken;
        payload.telegram_chat_id = telegramChatId;
      }
      
      const response = await axios.post(`${API}/setup`, payload);
      
      const successMsg = response.data.telegram_enabled 
        ? "API Keys y Telegram configurados correctamente" 
        : "API Keys configuradas correctamente";
      
      toast.success(successMsg);
      setIsConfigured(true);
      fetchPrices();
      fetchBalance();
    } catch (error) {
      toast.error("Error al configurar: " + error.response?.data?.detail);
    }
  };

  const handleStartBot = async () => {
    try {
      const response = await axios.post(`${API}/bot/start`, {
        strategy: "aggressive_scalping",
        symbols: ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
        max_trade_amount: 10.0,
        profit_target: 1.5,
        stop_loss: 0.5,
        use_percentage: true,
        balance_percentage: 5.0
      });
      
      toast.success("Bot de trading iniciado con reinversión automática del 5%");
      fetchBotStatus();
    } catch (error) {
      toast.error("Error al iniciar bot: " + error.response?.data?.detail);
    }
  };

  const handleStopBot = async () => {
    try {
      const response = await axios.post(`${API}/bot/stop`);
      toast.success("Bot de trading detenido");
      fetchBotStatus();
    } catch (error) {
      toast.error("Error al detener bot: " + error.response?.data?.detail);
    }
  };

  if (!isConfigured) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4" data-testid="setup-screen">
        <Toaster position="top-center" richColors />
        <Card className="w-full max-w-lg bg-[#0F0F11] border border-white/10 p-8">
          <div className="space-y-6">
            <div className="space-y-2">
              <h1 className="text-4xl font-black text-white tracking-tight" style={{ fontFamily: 'Chivo' }} data-testid="app-title">
                AlgoTrade X
              </h1>
              <p className="text-sm text-zinc-400 font-mono uppercase tracking-wider">Configuración Inicial</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs text-zinc-400 font-mono uppercase tracking-wider block mb-2">API KEY</label>
                <Input
                  type="text"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Ingresa tu Binance API Key"
                  className="bg-[#0A0A0A] border-white/10 text-white font-mono"
                  data-testid="api-key-input"
                />
              </div>

              <div>
                <label className="text-xs text-zinc-400 font-mono uppercase tracking-wider block mb-2">API SECRET</label>
                <Input
                  type="password"
                  value={apiSecret}
                  onChange={(e) => setApiSecret(e.target.value)}
                  placeholder="Ingresa tu Binance API Secret"
                  className="bg-[#0A0A0A] border-white/10 text-white font-mono"
                  data-testid="api-secret-input"
                />
              </div>

              <div className="flex items-center justify-between p-4 bg-[#0A0A0A] border border-white/10 rounded-sm">
                <span className="text-sm text-white font-mono">TESTNET MODE</span>
                <Switch
                  checked={isTestnet}
                  onCheckedChange={setIsTestnet}
                  data-testid="testnet-switch"
                />
              </div>

              <div className="border-t border-white/10 pt-4 mt-2">
                <label className="text-xs text-[#10B981] font-mono uppercase tracking-wider block mb-3">📱 TELEGRAM (OPCIONAL)</label>
                
                <div className="space-y-3">
                  <Input
                    type="text"
                    value={telegramToken}
                    onChange={(e) => setTelegramToken(e.target.value)}
                    placeholder="Telegram Bot Token"
                    className="bg-[#0A0A0A] border-white/10 text-white font-mono text-sm"
                    data-testid="telegram-token-input"
                  />
                  
                  <Input
                    type="text"
                    value={telegramChatId}
                    onChange={(e) => setTelegramChatId(e.target.value)}
                    placeholder="Tu Chat ID"
                    className="bg-[#0A0A0A] border-white/10 text-white font-mono text-sm"
                    data-testid="telegram-chatid-input"
                  />
                </div>
              </div>

              <Button
                onClick={handleSetupKeys}
                className="w-full bg-[#FCD535] hover:bg-[#FDE047] text-black font-bold rounded-sm h-12"
                data-testid="setup-submit-btn"
              >
                CONFIGURAR Y CONTINUAR
              </Button>

              <div className="p-4 bg-[#1A1A1D] border border-white/10 rounded-sm space-y-2">
                <p className="text-xs text-zinc-400 leading-relaxed" style={{ fontFamily: 'IBM Plex Sans' }}>
                  <strong className="text-white">Binance:</strong> Obtén tus API keys desde Binance → API Management. 
                  Activa permisos de "Enable Spot & Margin Trading". Para pruebas seguras, usa el Testnet.
                </p>
                <p className="text-xs text-zinc-400 leading-relaxed" style={{ fontFamily: 'IBM Plex Sans' }}>
                  <strong className="text-[#10B981]">Telegram:</strong> Habla con @BotFather para crear tu bot. 
                  Obtén tu Chat ID hablando con @userinfobot. Recibirás notificaciones de cada trade y reporte diario a las 23:59 UTC.
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  const dailyProfit = botStatus?.daily_profit || 0;
  const dailyGoal = 1000;
  const progressPct = Math.min((dailyProfit / dailyGoal) * 100, 100);

  return (
    <div className="min-h-screen bg-[#050505]" data-testid="trading-dashboard">
      <Toaster position="top-center" richColors />
      
      {/* Top Bar */}
      <div className="bg-black border-b border-white/10 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-black text-white tracking-tight" style={{ fontFamily: 'Chivo' }} data-testid="dashboard-title">
            AlgoTrade X
          </h1>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              {botStatus?.is_running && (
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" data-testid="bot-active-indicator"></span>
                  <span className="text-xs font-mono text-emerald-500 uppercase tracking-wider">BOT ACTIVO</span>
                </span>
              )}
              {!botStatus?.is_running && (
                <span className="text-xs font-mono text-zinc-400 uppercase tracking-wider">BOT INACTIVO</span>
              )}
            </div>
            
            {!botStatus?.is_running ? (
              <Button
                onClick={handleStartBot}
                className="bg-[#10B981] hover:bg-[#059669] text-white font-bold rounded-sm px-6"
                data-testid="start-bot-btn"
              >
                INICIAR BOT
              </Button>
            ) : (
              <Button
                onClick={handleStopBot}
                className="bg-[#EF4444] hover:bg-[#DC2626] text-white font-bold rounded-sm px-6"
                data-testid="stop-bot-btn"
              >
                DETENER BOT
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Daily Progress */}
          <div className="lg:col-span-4">
            <Card className="bg-[#0F0F11] border border-white/10 p-6" data-testid="daily-goal-widget">
              <div className="space-y-4">
                <div>
                  <p className="text-xs text-zinc-400 font-mono uppercase tracking-wider">PROGRESO DIARIO</p>
                  <div className="flex items-baseline gap-2 mt-2">
                    <span className="text-5xl font-black text-white font-mono" data-testid="daily-profit-metric">
                      ${dailyProfit.toFixed(2)}
                    </span>
                    <span className="text-zinc-400 text-sm font-mono">/ $1,000</span>
                  </div>
                </div>
                <Progress value={progressPct} className="h-2" data-testid="daily-progress-bar" />
                <p className="text-xs text-zinc-400 font-mono">
                  {progressPct.toFixed(1)}% completado
                </p>
              </div>
            </Card>
          </div>

          {/* Stats */}
          <div className="lg:col-span-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="bg-[#0F0F11] border border-white/10 p-6" data-testid="total-trades-card">
                <p className="text-xs text-zinc-400 font-mono uppercase tracking-wider">TRADES TOTALES</p>
                <p className="text-4xl font-black text-white font-mono mt-2" data-testid="total-trades-count">
                  {botStatus?.total_trades || 0}
                </p>
              </Card>

              <Card className="bg-[#0F0F11] border border-white/10 p-6" data-testid="winning-trades-card">
                <p className="text-xs text-zinc-400 font-mono uppercase tracking-wider">TRADES GANADORES</p>
                <p className="text-4xl font-black text-[#10B981] font-mono mt-2" data-testid="winning-trades-count">
                  {botStatus?.winning_trades || 0}
                </p>
              </Card>

              <Card className="bg-[#0F0F11] border border-white/10 p-6" data-testid="balance-card">
                <p className="text-xs text-zinc-400 font-mono uppercase tracking-wider">BALANCE USDT</p>
                <p className="text-4xl font-black text-white font-mono mt-2" data-testid="balance-amount">
                  ${botStatus?.balance?.toFixed(2) || '0.00'}
                </p>
              </Card>
            </div>
          </div>

          {/* Market Prices */}
          <div className="lg:col-span-12">
            <Card className="bg-[#0F0F11] border border-white/10 p-6" data-testid="market-prices-widget">
              <h2 className="text-lg font-bold text-white mb-4" style={{ fontFamily: 'Chivo' }}>PRECIOS DE MERCADO</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {prices.map((p) => (
                  <div key={p.symbol} className="bg-[#0A0A0A] border border-white/10 p-4 rounded-sm hover:bg-[#1A1A1D] transition-all" data-testid={`price-${p.symbol}`}>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-mono text-zinc-400">{p.symbol}</span>
                      <span className={`text-xs font-mono ${p.change_24h >= 0 ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                        {p.change_24h >= 0 ? '+' : ''}{p.change_24h?.toFixed(2)}%
                      </span>
                    </div>
                    <p className="text-2xl font-black text-white font-mono mt-2">${p.price?.toFixed(2)}</p>
                    <div className="mt-2 text-xs text-zinc-400 font-mono">
                      <div>H: ${p.high_24h?.toFixed(2)}</div>
                      <div>L: ${p.low_24h?.toFixed(2)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Price Chart */}
          <div className="lg:col-span-8">
            <Card className="bg-[#0F0F11] border border-white/10 p-6" data-testid="price-chart-widget">
              <h2 className="text-lg font-bold text-white mb-4" style={{ fontFamily: 'Chivo' }}>GRÁFICO DE PRECIOS</h2>
              <PriceChart prices={prices} />
            </Card>
          </div>

          {/* Balance */}
          <div className="lg:col-span-4">
            <Card className="bg-[#0F0F11] border border-white/10 p-6" data-testid="portfolio-balance-widget">
              <h2 className="text-lg font-bold text-white mb-4" style={{ fontFamily: 'Chivo' }}>BALANCE DE CARTERA</h2>
              <div className="space-y-2">
                {balance.slice(0, 5).map((b) => (
                  <div key={b.asset} className="flex items-center justify-between py-2 border-b border-white/5" data-testid={`balance-${b.asset}`}>
                    <span className="text-sm font-mono text-zinc-400">{b.asset}</span>
                    <span className="text-sm font-mono text-white">{b.total.toFixed(6)}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Recent Trades */}
          <div className="lg:col-span-12">
            <Card className="bg-[#0F0F11] border border-white/10 p-6" data-testid="recent-trades-table">
              <h2 className="text-lg font-bold text-white mb-4" style={{ fontFamily: 'Chivo' }}>TRADES RECIENTES</h2>
              <TradesTable trades={trades} />
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
