# AlgoTrade X - PRD

## Problem Statement
Build a fully autonomous crypto trading platform using Binance to maximize profits. Target: ~$1000/day starting with $200 capital. Includes daily Telegram notifications for profit and balance updates.

## Core Requirements
1. Connect to **real Binance Testnet** (`testnet.binance.vision`) - NO demo/mock mode
2. Balance must come from Binance API (`get_asset_balance`), NOT local calculations
3. Automatic buy/sell using RSI-based aggressive scalping strategy
4. Monitor top 30 cryptocurrencies
5. 5% compounding reinvestment per trade (dynamic, based on real balance)
6. Daily Telegram notifications (trade alerts + daily summary report at 23:59 UTC)
7. Bloomberg-terminal aesthetic dark UI

## Architecture
- **Frontend**: React + TailwindCSS + Shadcn/UI (port 3000)
- **Backend**: FastAPI + Motor (async MongoDB) (port 8001, proxied via /api)
- **Database**: MongoDB
- **Integrations**: Binance API (python-binance), Telegram Bot API (httpx)

## What's Been Implemented (April 2026)
- [x] FastAPI backend with all trading endpoints
- [x] React dashboard with Bloomberg-terminal aesthetics
- [x] RSI-based aggressive scalping strategy for 30 cryptos
- [x] 5% compound reinvestment logic
- [x] **Telegram notifications (WORKING)** - trade alerts, daily reports, bot status
- [x] Config persistence to MongoDB (survives restarts)
- [x] Auto-load config on server startup
- [x] **Real Binance Testnet client** (no demo fallback) - `AsyncClient(testnet=True)`
- [x] Clear geo-restriction error handling
- [x] Removed ALL demo/mock trading logic
- [x] WebSocket support for real-time updates
- [x] Daily report scheduler (APScheduler)
- [x] Frontend auto-detects existing config on page refresh

## Known Limitation
- Binance Testnet is **geo-restricted (HTTP 451)** from the Emergent preview server's IP. App works correctly when deployed on a server in a non-restricted location.

## Key Endpoints
- `POST /api/setup` - Save API keys + Telegram creds, init Binance & Telegram
- `GET /api/config/status` - Check if config exists
- `POST /api/bot/start` / `POST /api/bot/stop` - Control trading bot
- `GET /api/bot/status` - Current bot state
- `GET /api/market/prices` - Fetch live prices (requires Binance)
- `GET /api/account/balance` - Real Binance balance (requires Binance)
- `GET /api/trades/history` - Trade history from MongoDB
- `GET /api/stats/daily` - Daily trading statistics
- `POST /api/telegram/test` - Send test Telegram message
- `POST /api/telegram/daily-report` - Trigger daily report
- `POST /api/telegram/configure` - Configure Telegram separately

## Backlog
- P1: Robust error handling for Binance rate limits and connection drops
- P1: Dynamic reinvestment calculation from REAL fetched balance before each trade
- P2: More trading strategies (day trading, swing trading)
- P2: Advanced charting (candlestick charts, indicator overlays)
- P3: Portfolio analytics and performance graphs
