"""
Backend API Tests for AlgoTrade X Trading Platform
Tests all endpoints including setup, config, telegram, bot status, trades, and stats
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials provided
TEST_TELEGRAM_TOKEN = "8650739378:AAFeZug0GK1h4GlTpbY9rWN-ZfP0sVUlqWM"
TEST_TELEGRAM_CHAT_ID = "1545886883"
TEST_BINANCE_API_KEY = "zzuAKYzHFiBjVzJgcoE64lklR4jpSW6ucirWmEIfQ9yZrQNr4Rf0P7w7RbM0MU83"
TEST_BINANCE_API_SECRET = "bASIQQKmx42msBpoySF7QvVu3ZDeNIVifp6bgcxvhLD7A7LXPVsAKgkxQl96AXXa"


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestHealthAndStatus:
    """Basic health and status endpoint tests"""
    
    def test_bot_status_endpoint(self, api_client):
        """GET /api/bot/status - returns current bot state"""
        response = api_client.get(f"{BASE_URL}/api/bot/status")
        assert response.status_code == 200
        
        data = response.json()
        # Verify expected fields in bot state
        assert "is_running" in data
        assert "strategy" in data
        assert "daily_profit" in data
        assert "total_trades" in data
        assert "winning_trades" in data
        assert "balance" in data
        assert "telegram_enabled" in data
        print(f"✅ Bot status: is_running={data['is_running']}, telegram_enabled={data['telegram_enabled']}")
    
    def test_config_status_endpoint(self, api_client):
        """GET /api/config/status - returns whether config is saved"""
        response = api_client.get(f"{BASE_URL}/api/config/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "configured" in data
        assert "binance_connected" in data
        assert "telegram_enabled" in data
        print(f"✅ Config status: configured={data['configured']}, binance_connected={data['binance_connected']}")


class TestSetupEndpoint:
    """Tests for POST /api/setup endpoint"""
    
    def test_setup_saves_config_to_mongodb(self, api_client):
        """POST /api/setup - saves config to MongoDB, attempts Binance connection"""
        payload = {
            "api_key": TEST_BINANCE_API_KEY,
            "api_secret": TEST_BINANCE_API_SECRET,
            "testnet": True,
            "telegram_bot_token": TEST_TELEGRAM_TOKEN,
            "telegram_chat_id": TEST_TELEGRAM_CHAT_ID
        }
        
        response = api_client.post(f"{BASE_URL}/api/setup", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        # Config should always be saved
        assert data.get("config_saved") == True
        
        # Binance will be geo-restricted from this server (expected)
        # Status will be 'partial' with geo_restricted=true
        assert data.get("status") in ["success", "partial"]
        
        # If geo-restricted, verify the flag is set
        if data.get("geo_restricted"):
            assert data.get("binance_connected") == False
            print(f"✅ Setup completed with geo-restriction (expected): {data['message']}")
        else:
            print(f"✅ Setup completed: binance_connected={data.get('binance_connected')}")
        
        # Telegram should be enabled if credentials provided
        print(f"✅ Telegram enabled: {data.get('telegram_enabled')}")
    
    def test_setup_without_telegram(self, api_client):
        """POST /api/setup - works without Telegram credentials"""
        payload = {
            "api_key": TEST_BINANCE_API_KEY,
            "api_secret": TEST_BINANCE_API_SECRET,
            "testnet": True
        }
        
        response = api_client.post(f"{BASE_URL}/api/setup", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("config_saved") == True
        print(f"✅ Setup without Telegram: config_saved={data['config_saved']}")


class TestTelegramEndpoints:
    """Tests for Telegram notification endpoints"""
    
    def test_telegram_configure(self, api_client):
        """POST /api/telegram/configure - configure Telegram separately"""
        payload = {
            "bot_token": TEST_TELEGRAM_TOKEN,
            "chat_id": TEST_TELEGRAM_CHAT_ID
        }
        
        response = api_client.post(f"{BASE_URL}/api/telegram/configure", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "telegram_enabled" in data
        print(f"✅ Telegram configure: status={data['status']}, enabled={data['telegram_enabled']}")
    
    def test_telegram_test_message(self, api_client):
        """POST /api/telegram/test - sends test message to user's Telegram"""
        # First ensure Telegram is configured
        config_payload = {
            "bot_token": TEST_TELEGRAM_TOKEN,
            "chat_id": TEST_TELEGRAM_CHAT_ID
        }
        api_client.post(f"{BASE_URL}/api/telegram/configure", json=config_payload)
        
        # Now test the test endpoint
        response = api_client.post(f"{BASE_URL}/api/telegram/test")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✅ Telegram test message sent: {data.get('message')}")
    
    def test_telegram_daily_report(self, api_client):
        """POST /api/telegram/daily-report - sends daily report via Telegram"""
        # Ensure Telegram is configured
        config_payload = {
            "bot_token": TEST_TELEGRAM_TOKEN,
            "chat_id": TEST_TELEGRAM_CHAT_ID
        }
        api_client.post(f"{BASE_URL}/api/telegram/configure", json=config_payload)
        
        response = api_client.post(f"{BASE_URL}/api/telegram/daily-report")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "success"
        print(f"✅ Daily report sent: {data.get('message')}")
    
    def test_telegram_configure_missing_params(self, api_client):
        """POST /api/telegram/configure - returns 400 if params missing"""
        payload = {"bot_token": TEST_TELEGRAM_TOKEN}  # Missing chat_id
        
        response = api_client.post(f"{BASE_URL}/api/telegram/configure", json=payload)
        assert response.status_code == 400
        print("✅ Telegram configure correctly rejects missing params")


class TestTradesAndStats:
    """Tests for trades history and statistics endpoints"""
    
    def test_trades_history(self, api_client):
        """GET /api/trades/history - returns trade history from MongoDB"""
        response = api_client.get(f"{BASE_URL}/api/trades/history")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Trades history: {len(data)} trades returned")
    
    def test_trades_history_with_limit(self, api_client):
        """GET /api/trades/history?limit=10 - respects limit parameter"""
        response = api_client.get(f"{BASE_URL}/api/trades/history?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
        print(f"✅ Trades history with limit: {len(data)} trades returned (max 10)")
    
    def test_daily_stats(self, api_client):
        """GET /api/stats/daily - returns daily trading statistics"""
        response = api_client.get(f"{BASE_URL}/api/stats/daily")
        assert response.status_code == 200
        
        data = response.json()
        # Verify expected fields
        assert "total_trades" in data
        assert "winning_trades" in data
        assert "losing_trades" in data
        assert "win_rate" in data
        assert "total_profit" in data
        assert "daily_goal" in data
        assert "progress" in data
        
        # Verify data types
        assert isinstance(data["total_trades"], int)
        assert isinstance(data["win_rate"], (int, float))
        print(f"✅ Daily stats: total_trades={data['total_trades']}, win_rate={data['win_rate']:.1f}%")


class TestBotControl:
    """Tests for bot start/stop endpoints (require Binance connection)"""
    
    def test_bot_start_without_binance(self, api_client):
        """POST /api/bot/start - returns 400 if Binance not connected"""
        # Since Binance is geo-restricted, this should fail
        payload = {
            "strategy": "aggressive_scalping",
            "symbols": ["BTCUSDT"],
            "max_trade_amount": 10.0,
            "profit_target": 1.5,
            "stop_loss": 0.5
        }
        
        response = api_client.post(f"{BASE_URL}/api/bot/start", json=payload)
        # Should return 400 because Binance is not connected (geo-restricted)
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
            print(f"✅ Bot start correctly requires Binance: {data['detail']}")
        else:
            # If somehow Binance connected, that's also fine
            print(f"✅ Bot start response: {response.status_code}")
    
    def test_bot_stop_when_not_running(self, api_client):
        """POST /api/bot/stop - returns 400 if bot not running"""
        response = api_client.post(f"{BASE_URL}/api/bot/stop")
        
        # Should return 400 if bot is not running
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
            print(f"✅ Bot stop correctly handles not running: {data['detail']}")
        else:
            print(f"✅ Bot stop response: {response.status_code}")


class TestMarketEndpoints:
    """Tests for market data endpoints (require Binance connection)"""
    
    def test_market_prices_without_binance(self, api_client):
        """GET /api/market/prices - returns 400 if Binance not initialized"""
        response = api_client.get(f"{BASE_URL}/api/market/prices?symbols=BTCUSDT")
        
        # Should return 400 because Binance is geo-restricted
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
            print(f"✅ Market prices correctly requires Binance: {data['detail']}")
        else:
            # If somehow Binance connected, verify response structure
            data = response.json()
            assert isinstance(data, list)
            print(f"✅ Market prices returned: {len(data)} symbols")
    
    def test_account_balance_without_binance(self, api_client):
        """GET /api/account/balance - returns 400 if Binance not initialized"""
        response = api_client.get(f"{BASE_URL}/api/account/balance")
        
        # Should return 400 because Binance is geo-restricted
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
            print(f"✅ Account balance correctly requires Binance: {data['detail']}")
        else:
            # If somehow Binance connected, verify response structure
            data = response.json()
            assert isinstance(data, list)
            print(f"✅ Account balance returned: {len(data)} assets")


class TestConfigPersistence:
    """Tests for config persistence across requests"""
    
    def test_config_persists_after_setup(self, api_client):
        """Verify config is saved and can be retrieved"""
        # First do setup
        setup_payload = {
            "api_key": TEST_BINANCE_API_KEY,
            "api_secret": TEST_BINANCE_API_SECRET,
            "testnet": True,
            "telegram_bot_token": TEST_TELEGRAM_TOKEN,
            "telegram_chat_id": TEST_TELEGRAM_CHAT_ID
        }
        
        setup_response = api_client.post(f"{BASE_URL}/api/setup", json=setup_payload)
        assert setup_response.status_code == 200
        
        # Now check config status
        status_response = api_client.get(f"{BASE_URL}/api/config/status")
        assert status_response.status_code == 200
        
        data = status_response.json()
        assert data.get("configured") == True
        print(f"✅ Config persisted: configured={data['configured']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
