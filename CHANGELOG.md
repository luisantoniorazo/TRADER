# AlgoTrade X - Bitacora de Cambios

## Version 2.0 - Motor de Trading Optimizado (6 Abril 2026)
- Trailing Stop Loss: Si sube a +1.5%, el stop sube a +0.5% (protege ganancias)
- Filtro de Volumen: No compra criptos con volumen bajo (evita trampas)
- Confirmacion de Reversion: Espera que el precio empiece a subir antes de comprar
- Proteccion BTC: Si BTC cae >1.5% en 1h, no compra nada
- Velas de 5 minutos en vez de 1 minuto (menos ruido, mejores senales)
- Ratios mejorados: Moderado ahora target 2.5% / stop 1.2% (antes 1.5% / 0.5%)
- Conservador: target 4% / stop 2% | Agresivo: target 1.5% / stop 0.8%
- Score minimo 2 puntos + RSI + confirmacion para entrar a trade

## Version 1.8 - Inteligencia de Mercado (6 Abril 2026)
- Fear & Greed Index: Compra cuando hay miedo, evita comprar con codicia extrema
- Correlacion BTC: Si BTC cae fuerte, no compra altcoins para proteger capital
- MACD: Confirma tendencia alcista/bajista antes de operar
- Bollinger Bands: Detecta sobrecompra/sobreventa con bandas de volatilidad
- MA200: Confirma tendencia de largo plazo
- Sistema de scoring: Combina todas las senales para decidir con confianza alta/media/baja
- Panel visual en dashboard con 4 indicadores en tiempo real
- Se refresca cada ~60 segundos automaticamente

## Version 1.7 - Filtros de Fecha en Grafica (6 Abril 2026)
- Accesos rapidos: 1D, 7D, 30D, 90D, 180D, 1A (1 ano), TODO
- Selector de rango de fechas personalizado (fecha inicio - fecha fin)
- Muestra cantidad de dias filtrados
- Grafica de barras con ganancias/perdidas por dia
- Tooltip con estrategia, P&L, win rate y acumulado
- Cada trade guarda la estrategia con la que fue ejecutado

## Version 1.6 - Grafica de Ganancias Diarias (6 Abril 2026)
- Grafica de barras con ganancias/perdidas por dia (verde=ganancia, rojo=perdida)
- Muestra estrategia utilizada cada dia (Conservador, Moderado, Agresivo) con colores
- Tooltip con detalle: P&L del dia, acumulado total, trades, win rate, estrategia
- Acumulado total en la esquina superior derecha
- Leyenda de estrategias debajo de la grafica
- Endpoint: GET /api/stats/profit-history
- Cada trade ahora guarda la estrategia con la que fue ejecutado

## Version 1.5 - Venta Manual de Posiciones (5 Abril 2026)
- Panel "POSICIONES ABIERTAS" con tabla de todas las posiciones activas
- Boton "VENDER" individual por cada posicion con precio actual y P&L en tiempo real
- Boton "VENDER TODAS" para cerrar todas las posiciones de golpe
- Muestra: simbolo, precio entrada, precio actual, cantidad, invertido, valor actual, P&L
- Notificacion de Telegram al vender manualmente
- Endpoints: GET /api/positions/open, POST /api/positions/sell, POST /api/positions/sell-all

## Version 1.4 - Selector de Estrategias (5 Abril 2026)
- Selector de 3 perfiles de riesgo: Conservador, Moderado, Agresivo
- Cada estrategia muestra descripcion, parametros RSI, % de inversion, target y stop loss
- Se muestra siempre: cuando el bot esta activo se ve cual estrategia esta en uso
- Las no activas se ven opacas y no se pueden seleccionar mientras el bot corre

## Version 1.3 - Notificaciones Telegram Mejoradas (5 Abril 2026)
- Compras muestran: simbolo, precio, cantidad, inversion total
- Ventas muestran: precio entrada/salida, invertido, retirado, P&L en $ y %
- Badge "Made with Emergent" removido
- Titulo cambiado a "AlgoTrade X"

## Version 1.2 - Ordenes Reales en Binance (5 Abril 2026)
- Fix: trades solo se registran si Binance ejecuta la orden exitosamente
- Respeta filtros LOT_SIZE y MIN_NOTIONAL de Binance
- Usa precio real de ejecucion (fills) no estimado
- Telegram configure guarda credenciales en MongoDB permanentemente

## Version 1.1 - Despliegue en VPS (5 Abril 2026)
- App desplegada en DigitalOcean Amsterdam (188.166.35.189)
- HTTPS con certificado autofirmado
- Nginx como proxy reverso
- Telegram funcionando y verificado
- Binance Testnet conectado sin geo-restriccion

## Version 1.0 - Lanzamiento Inicial (5 Abril 2026)
- Eliminado modo Demo completamente
- Conexion real a Binance Testnet (AsyncClient testnet=True)
- Servicio de Telegram reescrito con httpx
- Config persistida en MongoDB (sobrevive reinicios)
- Auto-carga de config al iniciar servidor
- Dashboard estilo Bloomberg con 30 criptomonedas
- Estrategia de scalping agresivo con RSI
- Reinversion compuesta del 5%
