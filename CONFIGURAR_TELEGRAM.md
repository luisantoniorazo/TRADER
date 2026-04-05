# 📱 Guía Rápida: Configurar Telegram Correctamente

## ❌ Problema: No Llegan Notificaciones

**Causa:** El sistema muestra `telegram_enabled: false`

Esto significa que cuando configuraste inicialmente, NO pegaste el Bot Token y Chat ID, o hubo un error al guardarlos.

---

## ✅ Solución: Reconfigura con Telegram

### Paso 1: Obtén tus Credenciales de Telegram

#### A. Bot Token (@BotFather)

1. Abre Telegram
2. Busca: `@BotFather`
3. Envía: `/newbot`
4. Nombre del bot: `Mi Bot de Trading` (o el que quieras)
5. Username: `mi_trading_bot_123_bot` (debe terminar en "bot")
6. **COPIA EL TOKEN** que te da (se ve así):
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567
   ```

#### B. Chat ID (@userinfobot)

1. En Telegram, busca: `@userinfobot`
2. Envía: `/start`
3. **COPIA EL NÚMERO** que dice "Id:" (se ve así):
   ```
   123456789
   ```

#### C. Activa tu Bot

1. Busca tu bot en Telegram (el username que creaste)
2. Envía: `/start`
3. ¡Listo!

---

### Paso 2: Reconfigura la Aplicación

**IMPORTANTE:** Debes reconfigurar desde cero para que Telegram se active.

1. **Detén el bot:**
   - Dashboard → Click "DETENER BOT"
   - Espera a que diga "BOT INACTIVO"

2. **Cierra sesión o recarga:**
   - Presiona F5 o refresca la página
   - O limpia el localStorage del navegador

3. **Configura de nuevo:**
   ```
   API Key: demo
   API Secret: demo
   TESTNET MODE: ✅ ON
   
   📱 TELEGRAM (OPCIONAL):
   Telegram Bot Token: [PEGA TU TOKEN AQUÍ]
   Tu Chat ID: [PEGA TU ID AQUÍ]
   ```

4. **Click "CONFIGURAR Y CONTINUAR"**

5. **Verifica el mensaje:**
   - Debe decir: **"API Keys y Telegram configurados correctamente"**
   - Si NO menciona Telegram, algo salió mal

6. **Verifica el estado:**
   ```
   https://auto-trader-222.preview.emergentagent.com/api/bot/status
   ```
   - Debe decir: `"telegram_enabled": true`
   - Si dice `false`, repite el proceso

---

### Paso 3: Inicia el Bot

1. Click **"INICIAR BOT"**
2. **Deberías recibir INMEDIATAMENTE** en Telegram:
   ```
   🚀 Bot de Trading Iniciado

   Estado: Activo ✅
   Estrategia: aggressive_scalping - Reinversión: 5% del saldo

   🔄 Reinversión Automática: 5% del saldo por trade
   💰 Crecimiento Compuesto: Las ganancias se reinvierten automáticamente

   El bot está monitoreando el mercado y ejecutará trades automáticamente.
   ```

3. **Si NO recibes este mensaje:**
   - Verifica que enviaste `/start` a tu bot
   - Verifica que el Chat ID sea correcto
   - Verifica que el Bot Token sea correcto

---

## 🧪 Prueba Manual de Telegram

Puedes probar si Telegram funciona sin iniciar el bot:

```bash
# Desde la terminal (yo lo hago por ti)
curl -X POST "https://auto-trader-222.preview.emergentagent.com/api/telegram/test"
```

Deberías recibir:
```
🤖 Prueba de Notificación

✅ Telegram configurado correctamente!
```

---

## 🎯 Checklist

Después de reconfigurar:

- [ ] Recibí el mensaje de "Bot de Trading Iniciado" en Telegram
- [ ] El estado del bot dice `telegram_enabled: true`
- [ ] El mensaje de configuración mencionó "Telegram configurados correctamente"

---

## 📊 Lo Que Recibirás en Telegram

### Cuando el bot inicia:
```
🚀 Bot de Trading Iniciado
Estado: Activo ✅
...
```

### En cada COMPRA:
```
🟢 Trade Ejecutado

Símbolo: BTCUSDT
Tipo: BUY
Precio: $45,230.50
Cantidad: 0.001106

⏰ 2026-04-05 17:30:42 UTC
```

### En cada VENTA:
```
🔴 Trade Ejecutado

Símbolo: BTCUSDT
Tipo: SELL
Precio: $45,908.75
Cantidad: 0.001106

💰 Ganancia/Pérdida: $0.75

⏰ 2026-04-05 17:45:18 UTC
```

### Reporte Diario (23:59 UTC):
```
📊 Reporte Diario de Trading
════════════════════════

📈 Ganancia del Día: $3.54
💰 Saldo Actual: $1,003.54

Estadísticas:
• Trades Totales: 5
• Trades Ganadores: 3
• Win Rate: 60.0%
...
```

---

## ⚠️ Errores Comunes

### 1. "Unauthorized"
- Tu Bot Token es incorrecto
- Solución: Genera uno nuevo con @BotFather

### 2. "Bad Request: chat not found"
- Tu Chat ID es incorrecto
- Solución: Verifica con @userinfobot

### 3. "Forbidden: bot was blocked by the user"
- Bloqueaste tu bot
- Solución: Desbloquéalo y envía /start

### 4. No recibo nada pero no hay errores
- No enviaste /start a tu bot
- Solución: Búscalo en Telegram y envía /start

---

## 🚀 Resumen Rápido

1. **@BotFather** → `/newbot` → Copia token
2. **@userinfobot** → `/start` → Copia ID
3. **Tu bot** → Envía `/start`
4. **Recarga la app** → Configura con Telegram → Inicia bot
5. **Recibes notificación** inmediata de inicio ✅

---

**¡Con Telegram configurado correctamente recibirás cada trade en tiempo real!** 📱💰
