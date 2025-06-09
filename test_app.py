import unittest
from datetime import datetime, timezone
import time
from app import create_app, db
from app.models.prop_firm import PropFirm
from app.models.signal import Signal
from config import TestingConfig


class TestFlaskApp(unittest.TestCase):
    HARDCODED_TRADE_MSG = '"strategy":"Heiken-Ashi CE LSMA [v5.1]", "order":"sell", "contracts":149.949, "ticker":"RUNEUSDT.P", "position_size":-149.949'

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Create tables
        db.create_all()

        # Clear only the test data we're about to create
        PropFirm.query.filter(PropFirm.name.like("Test Prop Firm%")).delete()
        db.session.commit()

        # add two prop firms
        response = self.client.post(
            "/prop_firms/", json={"name": "Test Prop Firm", "full_balance": 100000}
        )
        data = response.get_json()
        self.prop_firm_id = data["prop_firm_id"]

        response = self.client.post(
            "/prop_firms/", json={"name": "Test Prop Firm 2", "full_balance": 100000}
        )
        data = response.get_json()
        self.prop_firm_id_2 = data["prop_firm_id"]

        # add two trades
        response = self.client.post("/trades/", data=self.HARDCODED_TRADE_MSG)
        data = response.get_json()
        self.btc_trade_id = data["trade_id"]

        response = self.client.post("/trades/", data=self.HARDCODED_TRADE_MSG)
        data = response.get_json()
        self.rune_trade_id = data["trade_id"]

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_hello_endpoint(self):
        response = self.client.get("/")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["message"], "Hello, World!")

    def test_health_endpoint(self):
        response = self.client.get("/health")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "healthy")

    def test_mt_string(self):
        response = self.client.post("/trades", data=self.HARDCODED_TRADE_MSG)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")

        # get trade by id
        response = self.client.get(f'/trades/{data["trade_id"]}')
        data = response.get_json()

        # Verify trade data]
        self.assertEqual(data["strategy"], "Heiken-Ashi CE LSMA [v5.1]")
        self.assertEqual(data["order_type"], "sell")
        self.assertEqual(data["contracts"], 149.949)
        self.assertEqual(data["ticker"], "RUNEUSDT.P")
        self.assertEqual(data["position_size"], -149.949)

    def test_get_trades(self):
        # initial number of trades
        response = self.client.get("/trades/")
        initial_trades_data = response.get_json()
        initial_trade_count = len(initial_trades_data["trades"])

        # First add a trade
        trade_response = self.client.post("/trades/", data=self.HARDCODED_TRADE_MSG)
        trade_data = trade_response.get_json()
        local_trade_id = trade_data["trade_id"]

        # Get trades
        final_trades_response = self.client.get("/trades/")
        final_trades_data = final_trades_response.get_json()

        self.assertEqual(final_trades_response.status_code, 200)
        self.assertTrue("trades" in final_trades_data)
        self.assertEqual(len(final_trades_data["trades"]), initial_trade_count + 1)

        # the trade id should be in the trades
        self.assertTrue(
            local_trade_id in [trade["id"] for trade in final_trades_data["trades"]]
        )

    def test_get_prop_firms(self):
        # initial number of prop firms
        response = self.client.get("/prop_firms/")
        data = response.get_json()
        initial_prop_firm_count = len(data)

        # add a prop firm
        prop_firm_name = "Test Prop Firm " + str(initial_prop_firm_count + 1)
        prop_initial_full_balance = 100000
        response = self.client.post(
            "/prop_firms",
            json={"name": prop_firm_name, "full_balance": prop_initial_full_balance},
        )

        # final number of prop firms
        response = self.client.get("/prop_firms/")
        data = response.get_json()
        final_prop_firm_count = len(data)

        # the number of prop firms should be one more than the initial number
        self.assertEqual(response.status_code, 200)
        self.assertEqual(final_prop_firm_count, initial_prop_firm_count + 1)

        # the prop firm should be in the list

        # find the prop firm in the list
        prop_firm = next(
            (prop_firm for prop_firm in data if prop_firm["name"] == prop_firm_name),
            None,
        )
        self.assertIsNotNone(prop_firm)

        # the prop firm should have the correct full balance
        self.assertEqual(prop_firm["full_balance"], prop_initial_full_balance)

        # the prop firm should have the correct available balance
        self.assertEqual(prop_firm["available_balance"], prop_initial_full_balance)

        # the prop firm should have the correct downdraft percentage
        self.assertEqual(prop_firm["drawdown_percentage"], 1)

        # the prop firm should have the correct trades
        self.assertEqual(prop_firm["trades"], [])

    def test_add_prop_firm(self):
        # initial number of prop firms
        response = self.client.get("/prop_firms/")
        data = response.get_json()
        initial_prop_firm_count = len(data)
        prop_firm_name = "Test Prop Firm " + str(initial_prop_firm_count + 1)

        prop_firm_data = {
            "name": prop_firm_name,
            "full_balance": 100000,
        }
        response = self.client.post("/prop_firms/", json=prop_firm_data)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")

        # Wrap database query in app context
        with self.app_context:
            # the prop firm should be in the database
            prop_firm = PropFirm.query.filter_by(name=prop_firm_name).first()
            self.assertIsNotNone(prop_firm)
            self.assertEqual(prop_firm.full_balance, 100000)
            self.assertEqual(prop_firm.available_balance, 100000)
            self.assertEqual(prop_firm.drawdown_percentage, 1)

    def test_add_trade(self):
        # initial number of trades
        response = self.client.get("/trades/")
        data = response.get_json()
        initial_trade_count = len(data["trades"])

        # add a trade
        trade_response = self.client.post("/trades/", data=self.HARDCODED_TRADE_MSG)
        trade_data = trade_response.get_json()

        # the status code should be 200 and the response should contain the trade id
        self.assertEqual(trade_response.status_code, 200)
        self.assertTrue("trade_id" in trade_data)
        self.assertEqual(trade_data["trade_id"], initial_trade_count + 1)

        # the trade should be in the database
        with self.app_context:
            trade = Signal.query.filter_by(id=trade_data["trade_id"]).first()
            self.assertIsNotNone(trade)
            self.assertEqual(trade.strategy, "Heiken-Ashi CE LSMA [v5.1]")
            self.assertEqual(trade.order_type, "sell")
            self.assertEqual(trade.contracts, 149.949)
            self.assertEqual(trade.ticker, "RUNEUSDT.P")
            self.assertEqual(trade.position_size, -149.949)

    def test_when_a_trade_is_added_it_should_be_added_for_all_prop_firms(self):
        # add a trade
        trade_response = self.client.post("/trades/", data=self.HARDCODED_TRADE_MSG)
        trade_data = trade_response.get_json()
        trade_id = trade_data["trade_id"]

        # every time a trade is placed it should be automatically added for all the prop firms
        prop_firms_response = self.client.get("/prop_firms/")
        prop_firms_data = prop_firms_response.get_json()
        self.assertEqual(prop_firms_response.status_code, 200)

        # the trade id should be in all the prop firms
        for prop_firm in prop_firms_data:
            self.assertTrue(trade_id in prop_firm["trades"])

    def test_decrease_balance_size_on_trade_creation(self):
        # balance of the prop firm before the trade is created
        prop_firm_response = self.client.get(f"/prop_firms/{self.prop_firm_id}")
        prop_firm_data = prop_firm_response.get_json()
        initial_prop_firm_available_balance = prop_firm_data["available_balance"]

        # add a trade
        trade_position_size = -33.333
        update_trade_msg = f'"strategy":"Heiken-Ashi CE LSMA [v5.1]", "order":"sell", "contracts":149.949, "ticker":"RUNEUSDT.P", "position_size":{trade_position_size}'
        self.client.post("/trades/", data=update_trade_msg)

        # get the prop firm
        prop_firm_response = self.client.get(f"/prop_firms/{self.prop_firm_id}")
        prop_firm_data = prop_firm_response.get_json()

        # even if the trade has a negative position size, the number has to be
        # converted to positive before deduction
        expected_value = initial_prop_firm_available_balance - abs(trade_position_size)
        self.assertEqual(prop_firm_data["available_balance"], expected_value)

    def increase_balance_size_on_trade_deletion(self):
        # initial_prop_firm_available_balance
        prop_firm_response = self.client.get(f"/prop_firms/{self.prop_firm_id}")
        prop_firm_data = prop_firm_response.get_json()
        initial_prop_firm_available_balance = prop_firm_data["prop_firm"][
            "available_balance"
        ]

        # add a trade
        trade_position_size = -33.333
        trade_response = self.client.post(
            "/trades/",
            data=f'"strategy":"Heiken-Ashi CE LSMA [v5.1]", "order":"sell", "contracts":149.949, "ticker":"RUNEUSDT.P", "position_size":{trade_position_size}',
        )
        trade_data = trade_response.get_json()
        trade_id = trade_data["trade_id"]

        # delete the trade
        self.client.delete(f"/trades/{trade_id}")

        # get the prop firm
        prop_firm_response = self.client.get(f"/prop_firms/{self.prop_firm_id}")
        prop_firm_data = prop_firm_response.get_json()

        # the available balance should be the initial available balance plus the trade position size
        expected_value = initial_prop_firm_available_balance + abs(trade_position_size)
        self.assertEqual(
            prop_firm_data["prop_firm"]["available_balance"], expected_value
        )

    def test_get_PropFirmTrades(self):
        # initial number of trades
        response = self.client.get(f"/prop_firm/{self.prop_firm_id}/trades")
        data = response.get_json()
        initial_trade_count = len(data["trades"])

        # add a trade
        response = self.client.post("/trades/", data=self.HARDCODED_TRADE_MSG)
        data = response.get_json()
        trade_id = data["trade_id"]

        # get the trades for the prop firm
        response = self.client.get(f"/prop_firm/{self.prop_firm_id}/trades")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue("trades" in data)
        self.assertEqual(len(data["trades"]), initial_trade_count + 1)
        self.assertTrue(trade_id in [trade["trade_id"] for trade in data["trades"]])

    def test_when_a_prop_firm_is_deleted_its_trades_should_not_be_deleted(self):
        # add a temporary prop firm
        number_of_prop_firms = len(self.client.get("/prop_firms/").get_json())

        prop_firm_name = "Test Prop Firm " + str(number_of_prop_firms + 1)
        response = self.client.post(
            "/prop_firms/", json={"name": prop_firm_name, "full_balance": 100000}
        )
        data = response.get_json()
        prop_firm_id = data["prop_firm_id"]

        # add a trade to the prop firm
        response = self.client.post("/trades/", data=self.HARDCODED_TRADE_MSG)
        data = response.get_json()
        trade_id = data["trade_id"]

        # delete the prop firm
        response = self.client.delete(f"/prop_firms/{prop_firm_id}")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")

        # get all the trades deleted for the prop firm
        response = self.client.get(f"/prop_firm/{prop_firm_id}/trades")
        data = response.get_json()

        # assert that the trade is still in the database
        with self.app_context:
            trade = Signal.query.filter_by(id=trade_id).first()
            self.assertIsNotNone(trade)

    def test_upsert_prop_firm_info(self):
        # add a prop firm is not needed because the prop firm is already created in the setup

        # get the current number of PropFirms
        number_of_prop_firms = len(self.client.get("/prop_firms/").get_json())

        # create a prop firm object to update
        test_prop_firm_object = {
            "name": f"Test Prop Firm {number_of_prop_firms + 1}",
            "full_balance": 100000,
            "available_balance": 100000,
            "drawdown_percentage": 1,
            "is_active": True,
            "username": f"test_username_{number_of_prop_firms + 1}",
            "password": f"test_password_{number_of_prop_firms + 1}",
            "ip_address": f"test_ip_address_{number_of_prop_firms + 1}",
            "port": 1234,
            "platform_type": f"test_platform_type_{number_of_prop_firms + 1}",
        }

        # current time
        current_time = datetime.now(timezone.utc)
        time.sleep(2)

        # update the prop firm
        response = self.client.put(
            f"/prop_firms/{self.prop_firm_id}", json=test_prop_firm_object
        )
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")

        # get the prop firm
        response = self.client.get(f"/prop_firms/{self.prop_firm_id}")
        prop_firm_data = response.get_json()
        self.assertEqual(
            prop_firm_data["name"], f"Test Prop Firm {number_of_prop_firms + 1}"
        )
        self.assertEqual(prop_firm_data["full_balance"], 100000)
        self.assertEqual(prop_firm_data["available_balance"], 100000)
        self.assertEqual(prop_firm_data["drawdown_percentage"], 1)
        self.assertEqual(prop_firm_data["is_active"], True)
        self.assertGreater(current_time.isoformat(), prop_firm_data["created_at"])
        self.assertEqual(
            prop_firm_data["username"], f"test_username_{number_of_prop_firms + 1}"
        )
        self.assertEqual(
            prop_firm_data["password"], f"test_password_{number_of_prop_firms + 1}"
        )
        self.assertEqual(
            prop_firm_data["ip_address"], f"test_ip_address_{number_of_prop_firms + 1}"
        )
        self.assertEqual(prop_firm_data["port"], 1234)
        self.assertEqual(
            prop_firm_data["platform_type"],
            f"test_platform_type_{number_of_prop_firms + 1}",
        )

    def test_the_trade_update_should_update_all_the_trades(self):
        # when a new trade update message is received, it should match all the
        #  associated trades based on the ticker, strategy, order type and position size
        # and update the trades with the new data
        new_strategy = f"Heiken-Ashi CE LSMA [v5.1] {datetime.now().isoformat()}"
        new_order = "buy"
        new_contracts = 1500.0
        new_ticker = "RUNEUSDT.P"
        new_position_size = -1500.0
        existing_trade_msg = f'"strategy":"{new_strategy}", \
            "order":"{new_order}", "contracts":500, \
            "ticker":"{new_ticker}", "position_size":{new_position_size}'

        # add a trade
        response = self.client.post("/trades/", data=existing_trade_msg)
        data = response.get_json()
        trade_id = data["trade_id"]

        # update the trade
        update_obj = {
            "strategy": new_strategy,
            "order": new_order,
            "contracts": new_contracts,
            "ticker": new_ticker,
            "position_size": new_position_size,
        }
        response = self.client.put("/trades_associations/", json=update_obj)
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        updated_trade_ids = data["updated_trades"]
        self.assertEqual(len(updated_trade_ids), 1)
        self.assertEqual(updated_trade_ids[0], trade_id)

        # get the trade
        response = self.client.get(f"/trades/{trade_id}")
        data = response.get_json()

        # get the prop firms
        response = self.client.get("/prop_firms/")
        prop_firms_data = response.get_json()

        # get the trade and check the updates for all the prop firms
        for prop_firm in prop_firms_data:
            response = self.client.get(f'/prop_firm/{prop_firm["id"]}/trades')
            data = response.get_json()
            for trade in data["trades"]:
                if trade["trade_id"] == trade_id:
                    self.assertEqual(trade["strategy"], new_strategy)
                    self.assertEqual(trade["order_type"], new_order)
                    self.assertEqual(trade["contracts"], new_contracts)
                    self.assertEqual(trade["ticker"], new_ticker)
                    self.assertEqual(trade["position_size"], new_position_size)

        # in the trades association table, only the trade with this ID should have that position size
        response = self.client.get("/trades_associations/")
        associated_trades = response.get_json()
        for trade in associated_trades:
            if trade["id"] == trade_id:
                self.assertEqual(trade["position_size"], new_position_size)
            else:
                self.assertNotEqual(trade["position_size"], new_position_size)


if __name__ == "__main__":
    unittest.main()
