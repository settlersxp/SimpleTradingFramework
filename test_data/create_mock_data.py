import requests
from time import sleep

BASE_URL = "http://localhost:3100"

def create_mock_data():
    # Create prop firms
    prop_firms = [
        {
            "name": "Alpha Trading",
            "full_balance": 100000.0
        },
        {
            "name": "Beta Capital",
            "full_balance": 250000.0
        }
    ]

    # Create trades (using MT string format as expected by the API)
    trades = [
        '"strategy":"Heiken-Ashi CE LSMA [v5.1]", "order":"sell", "contracts":149.949, "ticker":"RUNEUSDT.P", "position_size":-149.949',
        '"strategy":"Heiken-Ashi CE LSMA [v5.1]", "order":"sell", "contracts":149.949, "ticker":"BTCUSDT.P", "position_size":-149.949',
        '"strategy":"Moving Average","order":"SELL","contracts":3.0,"ticker":"MSFT" ,"position_size":1500.0',
        '"strategy":"Breakout","order":"BUY","contracts":1.0,"ticker":"AMZN","position_size":3000.0'
    ]

    print("Creating prop firms...")
    for firm in prop_firms:
        response = requests.post(f"{BASE_URL}/prop_firms", json=firm)
        if response.status_code != 200:
            print(f"Error creating prop firm {firm['name']}: {response.json()}")
            return
        print(f"Created prop firm: {firm['name']}")
    
    print("\nCreating trades...")
    for trade in trades:
        response = requests.post(f"{BASE_URL}/trades", data=trade)
        if response.status_code != 200:
            print(f"Error creating trade: {response.json()}")
            return
        print(f"Created trade: {trade}")

    # Give the server a moment to process everything
    sleep(1)

    # Verify creation by getting all data
    print("\nVerifying creation...")
    
    prop_firms_response = requests.get(f"{BASE_URL}/prop_firms")
    trades_response = requests.get(f"{BASE_URL}/trades")
    
    if prop_firms_response.status_code == 200 and trades_response.status_code == 200:
        prop_firms_data = prop_firms_response.json()
        trades_data = trades_response.json()
        print("\nMock data created successfully!")
        print(f"Created {len(prop_firms_data['prop_firms'])} prop firms and {len(trades_data['trades'])} trades")
    else:
        print("Error verifying data creation")

if __name__ == "__main__":
    create_mock_data() 