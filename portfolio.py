import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
try:
    import yfinance as yf
    yfinance_available = True
except ImportError:
    yfinance_available = False
    st.error("yfinance not installed. Install with `pip install yfinance` for real-time prices.")

# Initialize dictionaries for current and sold portfolios
current_portfolio = {
    "stock_name": [],
    "stock_pur_price": [],
    "stock_cur_price": [],
    "quantity": [],
    "profit_loss": [],
    "percent_profit_loss": []
}

sold_portfolio = {
    "stock_name": [],
    "stock_pur_price": [],
    "stock_sold_price": [],
    "quantity": [],
    "booked_profit_loss": [],
    "percent_booked_profit_loss": []
}

# NIFTY 100 index data for April 2025 from search results
nifty100_data = {
    "date": ["2025-04-02", "2025-04-17"],
    "price": [23713.80, 24418.35]
}
nifty100_df = pd.DataFrame(nifty100_data)
nifty100_df["date"] = pd.to_datetime(nifty100_df["date"])

# Known NIFTY 100 stock prices (from, January 31, 2025)
known_prices = {
    "RELIANCE": 1289.15,
    "HDFCBANK": 1839.20,
    "TCS": 3668.00,
    "BHARTIARTL": 1721.20,
    "ICICIBANK": 1333.35,
    "SBIN": 776.15,
    "INFY": 1628.25,
    "BAJFINANCE": 8999.85,
    "HINDUNILVR": 2273.00,
    "ITC": 410.10
}

def load_portfolios():
    """Load existing portfolios from CSV files, handling missing columns and empty data."""
    global current_portfolio, sold_portfolio
    required_current_columns = ["stock_name", "stock_pur_price", "stock_cur_price", "quantity", "profit_loss"]
    required_sold_columns = ["stock_name", "stock_pur_price", "stock_sold_price", "quantity", "booked_profit_loss"]

    # Load current portfolio
    if os.path.exists("current_portfolio.csv"):
        try:
            df = pd.read_csv("current_portfolio.csv")
            if not df.empty and all(col in df.columns for col in required_current_columns):
                df = df[df["stock_name"] != "Total"]
                if not df.empty:
                    # Load required columns
                    current_portfolio["stock_name"] = df["stock_name"].tolist()
                    current_portfolio["stock_pur_price"] = df["stock_pur_price"].tolist()
                    current_portfolio["stock_cur_price"] = df["stock_cur_price"].tolist()
                    current_portfolio["quantity"] = df["quantity"].astype(int).tolist()
                    current_portfolio["profit_loss"] = df["profit_loss"].tolist()
                    # Handle percent_profit_loss
                    if "percent_profit_loss" in df.columns:
                        current_portfolio["percent_profit_loss"] = df["percent_profit_loss"].tolist()
                    else:
                        # Verify lists are non-empty and equal length
                        if (len(current_portfolio["stock_cur_price"]) > 0 and
                            len(current_portfolio["stock_cur_price"]) == len(current_portfolio["stock_pur_price"])):
                            current_portfolio["percent_profit_loss"] = [
                                ((cur - pur) / pur * 100) if pur > 0 else 0
                                for cur, pur in zip(current_portfolio["stock_cur_price"], current_portfolio["stock_pur_price"])
                            ]
                        else:
                            current_portfolio["percent_profit_loss"] = [0] * len(current_portfolio["stock_name"])
                else:
                    st.warning("current_portfolio.csv contains only 'Total' row or is empty. Starting with empty portfolio.")
                    current_portfolio = {k: [] for k in current_portfolio}
            else:
                st.warning("current_portfolio.csv is empty or missing required columns. Starting with empty portfolio.")
                current_portfolio = {k: [] for k in current_portfolio}
        except Exception as e:
            st.warning(f"Error loading current_portfolio.csv: {e}. Starting with empty portfolio.")
            current_portfolio = {k: [] for k in current_portfolio}
    
    # Load sold portfolio
    if os.path.exists("sold_portfolio.csv"):
        try:
            df = pd.read_csv("sold_portfolio.csv")
            if not df.empty and all(col in df.columns for col in required_sold_columns):
                df = df[df["stock_name"] != "Total"]
                if not df.empty:
                    # Load required columns
                    sold_portfolio["stock_name"] = df["stock_name"].tolist()
                    sold_portfolio["stock_pur_price"] = df["stock_pur_price"].tolist()
                    sold_portfolio["stock_sold_price"] = df["stock_sold_price"].tolist()
                    sold_portfolio["quantity"] = df["quantity"].astype(int).tolist()
                    sold_portfolio["booked_profit_loss"] = df["booked_profit_loss"].tolist()
                    # Handle percent_booked_profit_loss
                    if "percent_booked_profit_loss" in df.columns:
                        sold_portfolio["percent_booked_profit_loss"] = df["percent_booked_profit_loss"].tolist()
                    else:
                        # Verify lists are non-empty and equal length
                        if (len(sold_portfolio["stock_sold_price"]) > 0 and
                            len(sold_portfolio["stock_sold_price"]) == len(sold_portfolio["stock_pur_price"])):
                            sold_portfolio["percent_booked_profit_loss"] = [
                                ((sold - pur) / pur * 100) if pur > 0 else 0
                                for sold, pur in zip(sold_portfolio["stock_sold_price"], sold_portfolio["stock_pur_price"])
                            ]
                        else:
                            sold_portfolio["percent_booked_profit_loss"] = [0] * len(sold_portfolio["stock_name"])
                else:
                    st.warning("sold_portfolio.csv contains only 'Total' row or is empty. Starting with empty portfolio.")
                    sold_portfolio = {k: [] for k in sold_portfolio}
            else:
                st.warning("sold_portfolio.csv is empty or missing required columns. Starting with empty portfolio.")
                sold_portfolio = {k: [] for k in sold_portfolio}
        except Exception as e:
            st.warning(f"Error loading sold_portfolio.csv: {e}. Starting with empty portfolio.")
            sold_portfolio = {k: [] for k in sold_portfolio}

def save_portfolios():
    """Save current and sold portfolios to CSV files with totals and percentages."""
    current_df = pd.DataFrame(current_portfolio)
    if not current_df.empty:
        current_df[["stock_pur_price", "stock_cur_price", "profit_loss", "percent_profit_loss"]] = current_df[
            ["stock_pur_price", "stock_cur_price", "profit_loss", "percent_profit_loss"]
        ].round(2)
        current_df["current_value"] = current_df["stock_cur_price"] * current_df["quantity"]
        total_value = current_df["current_value"].sum()
        total_profit_loss = current_df["profit_loss"].sum()
        current_df["investment"] = current_df["stock_pur_price"] * current_df["quantity"]
        total_investment = current_df["investment"].sum()
        total_percent_profit_loss = (total_profit_loss / total_investment * 100) if total_investment > 0 else 0
        total_row = pd.DataFrame({
            "stock_name": ["Total"],
            "stock_pur_price": [None],
            "stock_cur_price": [None],
            "quantity": [None],
            "profit_loss": [total_profit_loss],
            "percent_profit_loss": [total_percent_profit_loss],
            "current_value": [total_value]
        })
        current_df = pd.concat([current_df, total_row], ignore_index=True)
        current_df.to_csv("current_portfolio.csv", index=False)
    
    sold_df = pd.DataFrame(sold_portfolio)
    if not sold_df.empty:
        sold_df[["stock_pur_price", "stock_sold_price", "booked_profit_loss", "percent_booked_profit_loss"]] = sold_df[
            ["stock_pur_price", "stock_sold_price", "booked_profit_loss", "percent_booked_profit_loss"]
        ].round(2)
        total_booked_profit_loss = sold_df["booked_profit_loss"].sum()
        sold_df["investment"] = sold_df["stock_pur_price"] * sold_df["quantity"]
        total_investment = sold_df["investment"].sum()
        total_percent_booked_profit_loss = (total_booked_profit_loss / total_investment * 100) if total_investment > 0 else 0
        total_row = pd.DataFrame({
            "stock_name": ["Total"],
            "stock_pur_price": [None],
            "stock_sold_price": [None],
            "quantity": [None],
            "booked_profit_loss": [total_booked_profit_loss],
            "percent_booked_profit_loss": [total_percent_booked_profit_loss]
        })
        sold_df = pd.concat([sold_df, total_row], ignore_index=True)
        sold_df.to_csv("sold_portfolio.csv", index=False)

def get_real_time_price(ticker):
    """Fetch real-time price using yfinance, return None if unavailable."""
    if yfinance_available:
        try:
            stock = yf.Ticker(f"{ticker}.NS")
            price = stock.history(period="1d")["Close"].iloc[-1]
            return round(price, 2)
        except Exception as e:
            st.warning(f"Failed to fetch real-time price for {ticker}: {e}")
            return None
    return None

def plot_portfolios(current_data, sold_data, nifty100_df):
    """Create a dual-panel plot: current portfolio profit/loss, sold portfolio booked profit/loss, and NIFTY 100 trend."""
    fig = plt.figure(figsize=(14, 10))
    
    ax1 = plt.subplot(2, 1, 1)
    current_df = pd.DataFrame(current_data)
    if not current_df.empty:
        colors = ['green' if pl >= 0 else 'red' for pl in current_df["profit_loss"]]
        ax1.bar(current_df["stock_name"], current_df["profit_loss"], color=colors, label="Unrealized Profit/Loss (₹)")
        ax1.set_xlabel("Stock Name")
        ax1.set_ylabel("Unrealized Profit/Loss (₹)")
        ax1.set_title("Current Portfolio Unrealized Profit/Loss")
        ax1.grid(True, axis="y", linestyle="--", alpha=0.7)
        ax1.legend()
    else:
        ax1.text(0.5, 0.5, "No Current Portfolio Data", horizontalalignment="center", verticalalignment="center")
        ax1.set_title("Current Portfolio Unrealized Profit/Loss")
    
    plt.xticks(rotation=45, ha="right")
    
    ax2 = plt.subplot(2, 1, 2)
    sold_df = pd.DataFrame(sold_data)
    if not sold_df.empty:
        colors = ['green' if pl >= 0 else 'red' for pl in sold_df["booked_profit_loss"]]
        ax2.bar(sold_df["stock_name"], sold_df["booked_profit_loss"], color=colors, label="Booked Profit/Loss (₹)", alpha=0.5)
        ax2.set_xlabel("Stock Name")
        ax2.set_ylabel("Booked Profit/Loss (₹)", color="black")
        ax2.tick_params(axis="y", labelcolor="black")
        ax2.grid(True, axis="y", linestyle="--", alpha=0.7)
        ax2.legend(loc="upper left")
    else:
        ax2.text(0.5, 0.5, "No Sold Portfolio Data", horizontalalignment="center", verticalalignment="center")
    
    ax3 = ax2.twinx()
    ax3.plot(nifty100_df["date"], nifty100_df["price"], color="blue", marker="o", label="NIFTY 100")
    ax3.set_ylabel("NIFTY 100 Index (₹)", color="blue")
    ax3.tick_params(axis="y", labelcolor="blue")
    ax3.legend(loc="upper right")
    
    ax2.set_title("Sold Portfolio Booked Profit/Loss vs. NIFTY 100 Trend (April 2025)")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    
    return fig

def print_market_trends():
    """Return a summary of recent market trends based on Indian market data."""
    trends = """
    **Market Trends (April 2025):**
    - NIFTY 100 index rose from 23,713.80 on April 2 to 24,418.35 on April 17, up 2.97%.
    - Strong rally on April 17, with Sensex up 1,509 points, driven by banks, auto, and pharma sectors.
    - Volatility persists due to escalating Indo-Pakistan tensions and global trade tariffs.
    - Bank of America expects RBI to cut repo rate to 6% in April, boosting market sentiment.
      *Source: Investing.com, Moneycontrol, Economic Times [April 2025]*
    """
    return trends

def remove_stock(portfolio_type="current"):
    """Remove a stock from the current or sold portfolio."""
    if portfolio_type == "current":
        portfolio = current_portfolio
        csv_file = "current_portfolio.csv"
        title = "Remove Stock from Current Portfolio"
    else:
        portfolio = sold_portfolio
        csv_file = "sold_portfolio.csv"
        title = "Remove Stock from Sold Portfolio"
    
    df = pd.DataFrame(portfolio)
    if df.empty:
        st.sidebar.write(f"No stocks to remove from {portfolio_type} portfolio.")
        return
    
    st.sidebar.subheader(title)
    stock_options = df["stock_name"].tolist()
    name = st.sidebar.selectbox(f"Select Stock to Remove from {portfolio_type.capitalize()} Portfolio", stock_options)
    
    if st.sidebar.button(f"Remove {portfolio_type.capitalize()} Stock"):
        idx = portfolio["stock_name"].index(name)
        for key in portfolio:
            portfolio[key].pop(idx)
        
        save_portfolios()
        st.sidebar.success(f"Removed {name} from {portfolio_type} portfolio.")
        st.experimental_rerun()

def main():
    st.title("NIFTY 100 Stock Portfolio Tracker")
    
    load_portfolios()
    
    st.sidebar.header("Portfolio Actions")
    action = st.sidebar.selectbox("Choose Action", ["Add Stock", "Sell Stock", "Update Price", "Remove Stock (Current)", "Remove Stock (Sold)"])
    
    st.header("Current Portfolio")
    current_df = pd.DataFrame(current_portfolio)
    if not current_df.empty:
        current_df[["stock_pur_price", "stock_cur_price", "profit_loss", "percent_profit_loss"]] = current_df[
            ["stock_pur_price", "stock_cur_price", "profit_loss", "percent_profit_loss"]
        ].round(2)
        current_df["current_value"] = (current_df["stock_cur_price"] * current_df["quantity"]).round(2)
        st.dataframe(current_df)
        total_value = current_df["current_value"].sum()
        total_profit_loss = current_df["profit_loss"].sum()
        current_df["investment"] = current_df["stock_pur_price"] * current_df["quantity"]
        total_investment = current_df["investment"].sum()
        total_percent_profit_loss = (total_profit_loss / total_investment * 100) if total_investment > 0 else 0
        st.write(f"**Total Current Value**: ₹{total_value:,.2f}")
        st.write(f"**Total Unrealized Profit/Loss**: ₹{total_profit_loss:,.2f}")
        st.write(f"**Total % Unrealized Profit/Loss**: {total_percent_profit_loss:.2f}%")
    else:
        st.write("No stocks in current portfolio.")
    
    st.header("Sold Portfolio")
    sold_df = pd.DataFrame(sold_portfolio)
    if not sold_df.empty:
        sold_df[["stock_pur_price", "stock_sold_price", "booked_profit_loss", "percent_booked_profit_loss"]] = sold_df[
            ["stock_pur_price", "stock_sold_price", "booked_profit_loss", "percent_booked_profit_loss"]
        ].round(2)
        st.dataframe(sold_df)
        total_booked_profit_loss = sold_df["booked_profit_loss"].sum()
        sold_df["investment"] = sold_df["stock_pur_price"] * sold_df["quantity"]
        total_investment = sold_df["investment"].sum()
        total_percent_booked_profit_loss = (total_booked_profit_loss / total_investment * 100) if total_investment > 0 else 0
        st.write(f"**Total Booked Profit/Loss**: ₹{total_booked_profit_loss:,.2f}")
        st.write(f"**Total % Booked Profit/Loss**: {total_percent_booked_profit_loss:.2f}%")
    else:
        st.write("No stocks in sold portfolio.")
    
    if action == "Add Stock":
        st.sidebar.subheader("Add New Stock")
        name = st.sidebar.text_input("Stock Name (Ticker, e.g., RELIANCE)", "").upper()
        pur_price = st.sidebar.number_input("Purchase Price per Share (₹)", min_value=0.0, step=0.01, value=0.0, format="%.2f")
        
        default_price = known_prices.get(name, 0.0)
        if yfinance_available and name:
            real_time_price = get_real_time_price(name)
            if real_time_price:
                default_price = real_time_price
                st.sidebar.write(f"Real-time price for {name}: ₹{default_price}")
        
        cur_price = st.sidebar.number_input(
            f"Current Price per Share (₹) [Known price for {name}: ₹{default_price} as of Jan 31, 2025]" if name in known_prices else "Current Price per Share (₹)",
            min_value=0.0, step=0.01, value=float(default_price), format="%.2f"
        )
        qty = st.sidebar.number_input("Quantity of Shares", min_value=1, step=1, value=1, format="%d")
        
        if st.sidebar.button("Add Stock"):
            if not name:
                st.sidebar.error("Stock name cannot be empty.")
            else:
                p_l = (cur_price - pur_price) * qty
                percent_p_l = ((cur_price - pur_price) / pur_price * 100) if pur_price > 0 else 0
                current_portfolio["stock_name"].append(name)
                current_portfolio["stock_pur_price"].append(pur_price)
                current_portfolio["stock_cur_price"].append(cur_price)
                current_portfolio["quantity"].append(qty)
                current_portfolio["profit_loss"].append(p_l)
                current_portfolio["percent_profit_loss"].append(percent_p_l)
                
                save_portfolios()
                st.sidebar.success(f"Added {name} to portfolio.")
                st.experimental_rerun()
    
    elif action == "Sell Stock":
        st.sidebar.subheader("Sell Stock")
        if current_df.empty:
            st.sidebar.write("No stocks to sell.")
        else:
            stock_options = current_df["stock_name"].tolist()
            name = st.sidebar.selectbox("Select Stock to Sell", stock_options)
            idx = current_portfolio["stock_name"].index(name)
            max_qty = current_portfolio["quantity"][idx]
            qty = st.sidebar.number_input("Quantity to Sell", min_value=1, max_value=max_qty, step=1, value=1, format="%d")
            sold_price = st.sidebar.number_input("Sold Price per Share (₹)", min_value=0.0, step=0.01, value=0.0, format="%.2f")
            
            if st.sidebar.button("Sell Stock"):
                pur_price = current_portfolio["stock_pur_price"][idx]

                booked_p_l = (sold_price - pur_price) * qty
                percent_booked_p_l = ((sold_price - pur_price) / pur_price * 100) if pur_price > 0 else 0
                
                if qty == current_portfolio["quantity"][idx]:
                    for key in current_portfolio:
                        current_portfolio[key].pop(idx)
                else:
                    current_portfolio["quantity"][idx] -= qty
                    current_portfolio["profit_loss"][idx] = (
                        current_portfolio["stock_cur_price"][idx] - current_portfolio["stock_pur_price"][idx]
                    ) * current_portfolio["quantity"][idx]
                    current_portfolio["percent_profit_loss"][idx] = (
                        (current_portfolio["stock_cur_price"][idx] - current_portfolio["stock_pur_price"][idx]) / current_portfolio["stock_pur_price"][idx] * 100
                    ) if current_portfolio["stock_pur_price"][idx] > 0 else 0
                
                sold_portfolio["stock_name"].append(name)
                sold_portfolio["stock_pur_price"].append(current_portfolio["stock_pur_price"][idx])
                sold_portfolio["stock_sold_price"].append(sold_price)
                sold_portfolio["quantity"].append(qty)
                sold_portfolio["booked_profit_loss"].append(booked_p_l)
                sold_portfolio["percent_booked_profit_loss"].append(percent_booked_p_l)
                
                save_portfolios()
                st.sidebar.success(f"Sold {qty} shares of {name}.")
                st.experimental_rerun()
    
    elif action == "Update Price":
        st.sidebar.subheader("Update Stock Price")
        if current_df.empty:
            st.sidebar.write("No stocks to update.")
        else:
            stock_options = current_df["stock_name"].tolist()
            name = st.sidebar.selectbox("Select Stock to Update", stock_options)
            idx = current_portfolio["stock_name"].index(name)
            default_price = known_prices.get(name, 0.0)
            if yfinance_available:
                real_time_price = get_real_time_price(name)
                if real_time_price:
                    default_price = real_time_price
                    st.sidebar.write(f"Real-time price for {name}: ₹{default_price}")
            
            cur_price = st.sidebar.number_input(
                f"New Current Price per Share (₹) [Known price for {name}: ₹{default_price} as of Jan 31, 2025]" if name in known_prices else "New Current Price per Share (₹)",
                min_value=0.0, step=0.01, value=float(default_price), format="%.2f"
            )
            
            if st.sidebar.button("Update Price"):
                current_portfolio["stock_cur_price"][idx] = cur_price
                current_portfolio["profit_loss"][idx] = (
                    cur_price - current_portfolio["stock_pur_price"][idx]
                ) * current_portfolio["quantity"][idx]
                current_portfolio["percent_profit_loss"][idx] = (
                    (cur_price - current_portfolio["stock_pur_price"][idx]) / current_portfolio["stock_pur_price"][idx] * 100
                ) if current_portfolio["stock_pur_price"][idx] > 0 else 0
                
                save_portfolios()
                st.sidebar.success(f"Updated price for {name}.")
                st.experimental_rerun()
    
    elif action == "Remove Stock (Current)":
        remove_stock(portfolio_type="current")
    
    elif action == "Remove Stock (Sold)":
        remove_stock(portfolio_type="sold")
    
    st.header("Portfolio Visualization")
    fig = plot_portfolios(current_portfolio, sold_portfolio, nifty100_df)
    st.pyplot(fig)
    
    st.header("Market Trends")
    st.markdown(print_market_trends())

if __name__ == "__main__":
    main()
