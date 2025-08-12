import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class StockPatternFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Price Pattern Finder")

        self.create_widgets()

    def create_widgets(self):
       
        self.top_frame = ttk.Frame(self.root, padding="10")
        self.top_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(self.top_frame, text="Enter Stock Symbol:").grid(row=0, column=0, sticky=tk.W)
        self.symbol_var = tk.StringVar()
        self.symbol_entry = ttk.Entry(self.top_frame, textvariable=self.symbol_var)
        self.symbol_entry.grid(row=0, column=1, sticky="we")

        ttk.Label(self.top_frame, text="Enter Period (e.g., 1mo, 3mo, 1y):").grid(row=1, column=0, sticky=tk.W)
        self.period_var = tk.StringVar(value="1mo")
        self.period_entry = ttk.Entry(self.top_frame, textvariable=self.period_var)
        self.period_entry.grid(row=1, column=1, sticky="we")

        ttk.Label(self.top_frame, text="Enter Interval (e.g., 1d, 1h):").grid(row=2, column=0, sticky=tk.W)
        self.interval_var = tk.StringVar(value="1d")
        self.interval_entry = ttk.Entry(self.top_frame, textvariable=self.interval_var)
        self.interval_entry.grid(row=2, column=1, sticky="we")

        self.fetch_button = ttk.Button(self.top_frame, text="Fetch Data & Find Patterns", command=self.fetch_and_find_patterns)
        self.fetch_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.top_frame.columnconfigure(1, weight=1)

        
        self.plot_frame = ttk.Frame(self.root, padding="10")
        self.plot_frame.grid(row=1, column=0, sticky="nsew")


        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

    def fetch_and_find_patterns(self):
        symbol = self.symbol_var.get().strip().upper()
        period = self.period_var.get().strip()
        interval = self.interval_var.get().strip()

        if not symbol or not period or not interval:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        try:
            data = yf.download(symbol, period=period, interval=interval)
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to download data: {e}")
            return

        if data is None or data.empty:            
            messagebox.showerror("Data Error", "No data found for the given inputs.")
            return

        self.plot_data(data, symbol)
        self.find_patterns(data)

    def plot_data(self, data, symbol):
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()

        closes = data['Close']
        if isinstance(closes, pd.DataFrame):
            closes = closes.iloc[:, 0]

        short_ma = closes.rolling(window=5).mean()
        long_ma = closes.rolling(window=20).mean()


        crossover_dates = []
        for i in range(1, len(closes)):
            if pd.isna(short_ma.iloc[i-1]) or pd.isna(long_ma.iloc[i-1]) or pd.isna(short_ma.iloc[i]) or pd.isna(long_ma.iloc[i]):
                continue

            short_prev = float(short_ma.iloc[i-1])
            short_curr = float(short_ma.iloc[i])
            long_prev = float(long_ma.iloc[i-1])
            long_curr = float(long_ma.iloc[i])

            if short_prev < long_prev and short_curr >= long_curr:
                crossover_dates.append((closes.index[i], closes.iloc[i], 'Golden'))
            elif short_prev > long_prev and short_curr <= long_curr:
                crossover_dates.append((closes.index[i], closes.iloc[i], 'Death'))

       
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(closes.index, closes, label='Close Price', color='blue')
        ax.plot(short_ma.index, short_ma, label='5-Day MA', color='orange')
        ax.plot(long_ma.index, long_ma, label='20-Day MA', color='green')

    
        for date, price, ctype in crossover_dates:
            if ctype == 'Golden':
                ax.scatter(date, price, color='gold', marker='^', s=100, label='Golden Cross' if 'Golden Cross' not in ax.get_legend_handles_labels()[1] else "")
            elif ctype == 'Death':
                ax.scatter(date, price, color='red', marker='v', s=100, label='Death Cross' if 'Death Cross' not in ax.get_legend_handles_labels()[1] else "")

        ax.set_title(f"{symbol} Close Price & Moving Averages")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        ax.grid(True)

        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.plot_frame.rowconfigure(0, weight=1)
        self.plot_frame.columnconfigure(0, weight=1)

        plt.close(fig)


    def find_patterns(self, data):
        closes = data['Close']

        if isinstance(closes, pd.DataFrame):
            closes = closes.iloc[:, 0]

        short_ma = closes.rolling(window=5).mean()
        long_ma = closes.rolling(window=20).mean()

        crossover_dates = []
        for i in range(1, len(closes)):
            
            if pd.isna(short_ma.iloc[i-1]) or pd.isna(long_ma.iloc[i-1]) or pd.isna(short_ma.iloc[i]) or pd.isna(long_ma.iloc[i]):
                continue  

            short_prev = float(short_ma.iloc[i-1])
            short_curr = float(short_ma.iloc[i])
            long_prev = float(long_ma.iloc[i-1])
            long_curr = float(long_ma.iloc[i])

            if short_prev < long_prev and short_curr >= long_curr:
                crossover_dates.append((closes.index[i], 'Golden Cross'))
            elif short_prev > long_prev and short_curr <= long_curr:
                crossover_dates.append((closes.index[i], 'Death Cross'))

        if not crossover_dates:
            messagebox.showinfo("Pattern Finder", "No moving average crossover patterns found.")
        else:
            msg = 'Detected patterns:\n'
            for date, pattern in crossover_dates:
                msg += f"{date.date()}: {pattern}\n"
            messagebox.showinfo("Pattern Finder", msg)


if __name__ == '__main__':
    root = tk.Tk()
    root.iconbitmap(r"mini project/Apple_Stock-512.ico")
    app = StockPatternFinderApp(root)
    root.mainloop()
