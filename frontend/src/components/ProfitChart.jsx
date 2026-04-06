import { useState, useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from "recharts";

const STRATEGY_LABELS = {
  aggressive_scalping: "Moderado",
  swing_trading: "Conservador",
  day_trading: "Agresivo"
};

const STRATEGY_COLORS = {
  aggressive_scalping: "#F59E0B",
  swing_trading: "#3B82F6",
  day_trading: "#EF4444"
};

const QUICK_FILTERS = [
  { label: "1D", days: 1 },
  { label: "7D", days: 7 },
  { label: "30D", days: 30 },
  { label: "90D", days: 90 },
  { label: "180D", days: 180 },
  { label: "1A", days: 365 },
  { label: "TODO", days: null },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null;
  
  const data = payload[0].payload;
  const stratLabel = STRATEGY_LABELS[data.strategy] || data.strategy;
  const stratColor = STRATEGY_COLORS[data.strategy] || "#F59E0B";
  
  return (
    <div className="bg-[#1A1A1D] border border-white/20 rounded-sm p-3 text-xs font-mono shadow-lg">
      <p className="text-zinc-400 mb-2">{label}</p>
      <p className={`font-bold text-sm ${data.profit >= 0 ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
        P&L: ${data.profit?.toFixed(2)}
      </p>
      <p className="text-zinc-300 mt-1">Acumulado: ${data.cumulative?.toFixed(2)}</p>
      <div className="flex items-center gap-2 mt-2 pt-2 border-t border-white/10">
        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: stratColor }}></span>
        <span style={{ color: stratColor }}>{stratLabel}</span>
      </div>
      <p className="text-zinc-500 mt-1">Trades: {data.trades} | Win Rate: {data.win_rate?.toFixed(0)}%</p>
    </div>
  );
};

export const ProfitChart = ({ data }) => {
  const [activeDays, setActiveDays] = useState(30);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const filteredData = useMemo(() => {
    if (!data || data.length === 0) return [];

    // Custom date range takes priority
    if (dateFrom || dateTo) {
      return data.filter(d => {
        if (dateFrom && d.date < dateFrom) return false;
        if (dateTo && d.date > dateTo) return false;
        return true;
      });
    }

    // Quick filter by days
    if (activeDays === null) return data;

    const now = new Date();
    const cutoff = new Date(now.getTime() - activeDays * 24 * 60 * 60 * 1000);
    const cutoffStr = cutoff.toISOString().slice(0, 10);
    return data.filter(d => d.date >= cutoffStr);
  }, [data, activeDays, dateFrom, dateTo]);

  const handleQuickFilter = (days) => {
    setActiveDays(days);
    setDateFrom("");
    setDateTo("");
  };

  const handleDateChange = (from, to) => {
    setDateFrom(from);
    setDateTo(to);
    setActiveDays(null);
  };

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-zinc-500 text-sm font-mono">
        Sin datos de ganancias todavia. Los datos apareceran cuando se cierren trades.
      </div>
    );
  }

  return (
    <div>
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        {/* Quick filters */}
        <div className="flex items-center bg-[#0A0A0A] border border-white/10 rounded-sm overflow-hidden">
          {QUICK_FILTERS.map((f) => (
            <button
              key={f.label}
              onClick={() => handleQuickFilter(f.days)}
              className={`px-3 py-1.5 text-xs font-mono transition-colors ${
                activeDays === f.days && !dateFrom && !dateTo
                  ? 'bg-white/10 text-white'
                  : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/5'
              }`}
              data-testid={`filter-${f.label}`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Date range inputs */}
        <div className="flex items-center gap-2">
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => handleDateChange(e.target.value, dateTo)}
            className="bg-[#0A0A0A] border border-white/10 rounded-sm px-2 py-1 text-xs font-mono text-zinc-400 focus:border-white/30 focus:outline-none"
            data-testid="date-from"
          />
          <span className="text-zinc-600 text-xs">-</span>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => handleDateChange(dateFrom, e.target.value)}
            className="bg-[#0A0A0A] border border-white/10 rounded-sm px-2 py-1 text-xs font-mono text-zinc-400 focus:border-white/30 focus:outline-none"
            data-testid="date-to"
          />
        </div>

        <span className="text-xs font-mono text-zinc-600">{filteredData.length} dia{filteredData.length !== 1 ? 's' : ''}</span>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={filteredData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff08" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 10, fill: '#71717a', fontFamily: 'monospace' }}
            tickFormatter={(v) => v.slice(5)}
            stroke="#ffffff10"
          />
          <YAxis 
            tick={{ fontSize: 10, fill: '#71717a', fontFamily: 'monospace' }}
            tickFormatter={(v) => `$${v}`}
            stroke="#ffffff10"
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={0} stroke="#ffffff20" />
          <Bar dataKey="profit" radius={[3, 3, 0, 0]} maxBarSize={40}>
            {filteredData.map((entry, index) => (
              <Cell 
                key={index}
                fill={entry.profit >= 0 ? '#10B981' : '#EF4444'}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      
      {/* Strategy legend */}
      <div className="flex items-center justify-center gap-6 mt-3 pt-3 border-t border-white/5">
        {Object.entries(STRATEGY_LABELS).map(([key, label]) => (
          <div key={key} className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: STRATEGY_COLORS[key] }}></span>
            <span className="text-xs font-mono text-zinc-500">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProfitChart;
