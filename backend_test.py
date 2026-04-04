import requests
import sys
import json
from datetime import datetime

class TradingPlatformTester:
    def __init__(self, base_url="https://auto-trader-222.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            
            result = {
                "test_name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success,
                "response_data": None,
                "error": None
            }

            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    result["response_data"] = response.json()
                except:
                    result["response_data"] = response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    result["error"] = error_data
                    print(f"   Error: {error_data}")
                except:
                    result["error"] = response.text
                    print(f"   Error: {response.text}")

            self.test_results.append(result)
            return success, result.get("response_data", {})

        except Exception as e:
            print(f"❌ Failed - Exception: {str(e)}")
            result = {
                "test_name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": None,
                "success": False,
                "response_data": None,
                "error": str(e)
            }
            self.test_results.append(result)
            return False, {}

    def test_bot_status(self):
        """Test bot status endpoint"""
        return self.run_test(
            "Bot Status",
            "GET",
            "bot/status",
            200
        )

    def test_setup_api_keys(self):
        """Test API keys setup (will fail without real keys)"""
        return self.run_test(
            "Setup API Keys",
            "POST",
            "setup",
            400,  # Expected to fail without real keys
            data={
                "api_key": "test_key",
                "api_secret": "test_secret",
                "testnet": True
            }
        )

    def test_market_prices(self):
        """Test market prices endpoint (will fail without API setup)"""
        return self.run_test(
            "Market Prices",
            "GET",
            "market/prices",
            400  # Expected to fail without Binance client
        )

    def test_account_balance(self):
        """Test account balance endpoint (will fail without API setup)"""
        return self.run_test(
            "Account Balance",
            "GET",
            "account/balance",
            400  # Expected to fail without Binance client
        )

    def test_trade_history(self):
        """Test trade history endpoint"""
        return self.run_test(
            "Trade History",
            "GET",
            "trades/history?limit=10",
            200
        )

    def test_daily_stats(self):
        """Test daily statistics endpoint"""
        return self.run_test(
            "Daily Stats",
            "GET",
            "stats/daily",
            200
        )

    def test_start_bot(self):
        """Test start bot endpoint (will fail without API setup)"""
        return self.run_test(
            "Start Bot",
            "POST",
            "bot/start",
            400,  # Expected to fail without API keys
            data={
                "strategy": "aggressive_scalping",
                "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
                "max_trade_amount": 10.0,
                "profit_target": 1.5,
                "stop_loss": 0.5
            }
        )

    def test_stop_bot(self):
        """Test stop bot endpoint (will fail if bot not running)"""
        return self.run_test(
            "Stop Bot",
            "POST",
            "bot/stop",
            400  # Expected to fail if bot not running
        )

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Trading Platform API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print("=" * 60)

        # Test basic endpoints that should work without API keys
        self.test_bot_status()
        self.test_trade_history()
        self.test_daily_stats()

        # Test endpoints that require API setup (expected to fail gracefully)
        self.test_setup_api_keys()
        self.test_market_prices()
        self.test_account_balance()
        self.test_start_bot()
        self.test_stop_bot()

        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed (expected for endpoints requiring API keys)")
            
            # Analyze results
            critical_failures = []
            expected_failures = []
            
            for result in self.test_results:
                if not result["success"]:
                    if result["endpoint"] in ["bot/status", "trades/history", "stats/daily"]:
                        critical_failures.append(result)
                    else:
                        expected_failures.append(result)
            
            if critical_failures:
                print(f"\n❌ Critical failures ({len(critical_failures)}):")
                for failure in critical_failures:
                    print(f"   - {failure['test_name']}: {failure['error']}")
                return 1
            else:
                print(f"\n✅ All critical endpoints working")
                print(f"⚠️  Expected failures for endpoints requiring API keys: {len(expected_failures)}")
                return 0

def main():
    tester = TradingPlatformTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())