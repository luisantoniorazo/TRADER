import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const PriceChart = ({ prices }) => {
  const chartData = prices.map((p, idx) => ({
    name: p.symbol,
    price: p.price,
    index: idx
  }));

  return (
    <div className="h-64" data-testid="price-chart">
      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="name" stroke="#71717A" style={{ fontSize: '12px', fontFamily: 'JetBrains Mono' }} />
            <YAxis stroke="#71717A" style={{ fontSize: '12px', fontFamily: 'JetBrains Mono' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0F0F11',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '2px',
                fontFamily: 'JetBrains Mono',
                fontSize: '12px'
              }}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#10B981"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorPrice)"
            />
          </AreaChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-full flex items-center justify-center text-zinc-400 text-sm font-mono">
          Cargando datos del mercado...
        </div>
      )}
    </div>
  );
};

export default PriceChart;
