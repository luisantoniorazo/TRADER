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
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-zinc-500 text-sm font-mono">
        Sin datos de ganancias todavia. Los datos apareceran cuando se cierren trades.
      </div>
    );
  }

  return (
    <div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
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
            {data.map((entry, index) => (
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
