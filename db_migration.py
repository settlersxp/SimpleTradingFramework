# There are 2 sqlite databases:
# - tradesv2.db: the main database
# - trades.db: the test database
# We want to migrate the trades.db to the tradesv2.db. I want to copy the content of the following tables:
# - prop_firms
# - users
# - user_prop_firm
# - user_trading_strategy
# - trading_strategies
# - prop_firm_trade_pair_association

import sqlite3


def migrate_trades_db_to_tradesv2_db():
    # Connect to the trades.db database
    conn = sqlite3.connect("trades.db")
    cursor = conn.cursor()

    # Connect to the tradesv2.db database
    conn_v2 = sqlite3.connect("tradesv2.db")
    cursor_v2 = conn_v2.cursor()

    # Copy the content of the prop_firms table
    cursor.execute("SELECT * FROM prop_firms")
    prop_firms = cursor.fetchall()
    cursor_v2.executemany(
        "INSERT INTO prop_firms (id, name, created_at, full_balance, available_balance, drawdown_percentage, is_active, username, password, ip_address, port, platform_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        prop_firms,
    )
    conn_v2.commit()

    # Copy the content of the users table
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor_v2.executemany(
        "INSERT INTO users (id, email, password, created_at, updated_at, logged_at, token) VALUES (?, ?, ?, ?, ?, ?, ?)",
        users,
    )
    conn_v2.commit()

    # Copy the content of the user_prop_firm table
    cursor.execute("SELECT * FROM user_prop_firm")
    user_prop_firm = cursor.fetchall()
    cursor_v2.executemany(
        "INSERT INTO user_prop_firm (user_id, prop_firm_id, created_at) VALUES (?, ?, ?)",
        user_prop_firm,
    )
    conn_v2.commit()

    # Copy the content of the user_trading_strategy table
    cursor.execute("SELECT * FROM user_trading_strategy")
    user_trading_strategy = cursor.fetchall()
    cursor_v2.executemany(
        "INSERT INTO user_trading_strategy (user_id, trading_strategy_id, created_at) VALUES (?, ?, ?)",
        user_trading_strategy,
    )
    conn_v2.commit()

    # Copy the content of the trading_strategies table
    cursor.execute("SELECT * FROM trading_strategies")
    trading_strategies = cursor.fetchall()
    cursor_v2.executemany(
        "INSERT INTO trading_strategies (id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        trading_strategies,
    )
    conn_v2.commit()

    # Copy the content of the prop_firm_trade_pair_association table
    cursor.execute("SELECT * FROM prop_firm_trade_pair_association")
    prop_firm_trade_pair_association = cursor.fetchall()
    cursor_v2.executemany(
        "INSERT INTO prop_firm_trade_pair_association (prop_firm_id, label, trade_pair_id) VALUES (?, ?, ?)",
        prop_firm_trade_pair_association,
    )
    conn_v2.commit()

    # Close the connections
    conn.close()
    conn_v2.close()


if __name__ == "__main__":
    migrate_trades_db_to_tradesv2_db()
