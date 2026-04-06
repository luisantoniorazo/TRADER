# AlgoTrade X - Bitacora de Cambios

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
