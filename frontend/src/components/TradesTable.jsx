const TradesTable = ({ trades }) => {
  const formatDate = (timestamp) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString('es-ES', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="overflow-x-auto" data-testid="trades-table">
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/10">
            <th className="text-left py-3 px-3 text-xs uppercase tracking-wider text-zinc-400 font-mono">SÍMBOLO</th>
            <th className="text-left py-3 px-3 text-xs uppercase tracking-wider text-zinc-400 font-mono">TIPO</th>
            <th className="text-right py-3 px-3 text-xs uppercase tracking-wider text-zinc-400 font-mono">ENTRADA</th>
            <th className="text-right py-3 px-3 text-xs uppercase tracking-wider text-zinc-400 font-mono">SALIDA</th>
            <th className="text-right py-3 px-3 text-xs uppercase tracking-wider text-zinc-400 font-mono">CANTIDAD</th>
            <th className="text-right py-3 px-3 text-xs uppercase tracking-wider text-zinc-400 font-mono">P&L</th>
            <th className="text-left py-3 px-3 text-xs uppercase tracking-wider text-zinc-400 font-mono">ESTADO</th>
            <th className="text-left py-3 px-3 text-xs uppercase tracking-wider text-zinc-400 font-mono">FECHA</th>
          </tr>
        </thead>
        <tbody>
          {trades.length === 0 ? (
            <tr>
              <td colSpan="8" className="text-center py-8 text-sm text-zinc-400 font-mono">
                No hay trades registrados
              </td>
            </tr>
          ) : (
            trades.map((trade, idx) => (
              <tr
                key={trade.id || idx}
                className="border-b border-white/5 hover:bg-white/5 transition-all"
                data-testid={`trade-row-${idx}`}
              >
                <td className="py-3 px-3 text-sm font-mono text-white">{trade.symbol}</td>
                <td className="py-3 px-3 text-sm font-mono text-zinc-400">{trade.side}</td>
                <td className="py-3 px-3 text-sm font-mono text-white text-right">
                  ${trade.entry_price?.toFixed(2)}
                </td>
                <td className="py-3 px-3 text-sm font-mono text-white text-right">
                  {trade.exit_price ? `$${trade.exit_price.toFixed(2)}` : '-'}
                </td>
                <td className="py-3 px-3 text-sm font-mono text-white text-right">
                  {trade.quantity?.toFixed(6)}
                </td>
                <td className={`py-3 px-3 text-sm font-mono text-right ${
                  trade.profit_loss > 0 ? 'text-[#10B981]' : trade.profit_loss < 0 ? 'text-[#EF4444]' : 'text-zinc-400'
                }`}>
                  {trade.profit_loss !== null && trade.profit_loss !== undefined
                    ? `${trade.profit_loss >= 0 ? '+' : ''}$${trade.profit_loss.toFixed(2)}`
                    : '-'}
                </td>
                <td className="py-3 px-3 text-sm font-mono">
                  <span className={`px-2 py-1 rounded-sm text-xs ${
                    trade.status === 'open' ? 'bg-[#3B82F6]/20 text-[#3B82F6]' : 'bg-zinc-800 text-zinc-400'
                  }`}>
                    {trade.status === 'open' ? 'ABIERTO' : 'CERRADO'}
                  </span>
                </td>
                <td className="py-3 px-3 text-sm font-mono text-zinc-400">
                  {formatDate(trade.timestamp)}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default TradesTable;
