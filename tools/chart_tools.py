"""
Stock Chart Visualization Tools

This module provides functions to generate historical stock charts using matplotlib.

Features:
    - Price history charts (line/candlestick)
    - Volume bars
    - Multi-stock comparison
    - Moving averages (MA50, MA200)
    - Customizable timeframes

Example:
    >>> from tools.chart_tools import ChartTools
    >>> charts = ChartTools()
    >>> chart_path = charts.plot_stock_history("NVDA", period="1y")
    >>> # Saves chart to charts/NVDA_1y.png
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import os
import logging

logger = logging.getLogger(__name__)

# Chart configuration
CHART_DIR = "charts"
FIGSIZE = (14, 8)
DPI = 100
STYLE = 'seaborn-v0_8-darkgrid'


class ChartTools:
    """
    Tools for generating stock price charts.
    
    This class provides methods to create various types of financial charts
    using matplotlib and yfinance data.
    
    Attributes:
        chart_dir (str): Directory where charts are saved
    
    Example:
        >>> charts = ChartTools()
        >>> path = charts.plot_stock_history("AAPL", period="6mo")
        >>> print(f"Chart saved to: {path}")
    """
    
    def __init__(self, chart_dir: str = CHART_DIR):
        """Initialize chart tools.
        
        Args:
            chart_dir: Directory to save charts (default: "charts/")
        """
        self.chart_dir = chart_dir
        
        # Create charts directory if it doesn't exist
        os.makedirs(self.chart_dir, exist_ok=True)
        logger.info(f"Chart directory: {os.path.abspath(self.chart_dir)}")
    
    def plot_stock_history(
        self, 
        ticker: str, 
        period: str = "1y",
        show_ma: bool = True,
        show_volume: bool = True
    ) -> str:
        """
        Generate historical price chart for a stock.
        
        Creates a chart showing:
        - Price line (closing prices)
        - Moving averages (MA50, MA200) if enabled
        - Volume bars if enabled
        
        Args:
            ticker: Stock ticker symbol (e.g., "NVDA", "AAPL")
            period: Time period ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max")
            show_ma: Whether to show moving averages
            show_volume: Whether to show volume bars
        
        Returns:
            Path to saved chart image
        
        Example:
            >>> charts = ChartTools()
            >>> path = charts.plot_stock_history("NVDA", period="1y", show_ma=True)
            >>> # Returns: "charts/NVDA_1y.png"
        """
        try:
            logger.info(f"Generating chart for {ticker} ({period})")
            
            # Fetch data from yfinance
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, auto_adjust=False)
            
            if hist.empty:
                raise ValueError(f"No data available for {ticker}")
            
            logger.info(f"Fetched {len(hist)} data points for {ticker}")
            
            # Create figure with subplots
            if show_volume:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=FIGSIZE, 
                                               gridspec_kw={'height_ratios': [3, 1]})
            else:
                fig, ax1 = plt.subplots(1, 1, figsize=FIGSIZE)
            
            # Plot price
            ax1.plot(hist.index, hist['Close'], label='Close Price', 
                    color='#2E86DE', linewidth=2)
            
            # Plot moving averages
            if show_ma and len(hist) >= 50:
                ma50 = hist['Close'].rolling(window=50).mean()
                ax1.plot(hist.index, ma50, label='MA50', 
                        color='#FF6B6B', linestyle='--', alpha=0.7)
                
                if len(hist) >= 200:
                    ma200 = hist['Close'].rolling(window=200).mean()
                    ax1.plot(hist.index, ma200, label='MA200', 
                            color='#4ECDC4', linestyle='--', alpha=0.7)
            
            # Formatting
            ax1.set_title(f'{ticker.upper()} - Price History ({period})', 
                         fontsize=16, fontweight='bold')
            ax1.set_ylabel('Price (USD)', fontsize=12)
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)
            
            # Format x-axis dates
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
            
            # Volume subplot
            if show_volume:
                # Create color list based on price movement
                colors = []
                for idx in range(len(hist)):
                    if hist['Close'].iloc[idx] >= hist['Open'].iloc[idx]:
                        colors.append('#26A69A')  # Green for up days
                    else:
                        colors.append('#EF5350')  # Red for down days
                
                ax2.bar(hist.index, hist['Volume'], color=colors, alpha=0.6)
                ax2.set_ylabel('Volume', fontsize=12)
                ax2.set_xlabel('Date', fontsize=12)
                ax2.grid(True, alpha=0.3)
                
                # Format volume numbers (M for millions)
                ax2.yaxis.set_major_formatter(
                    plt.FuncFormatter(lambda x, p: f'{x/1e6:.0f}M')
                )
            else:
                ax1.set_xlabel('Date', fontsize=12)
            
            # Rotate dates
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
            if show_volume:
                plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save chart
            filename = f"{ticker.upper()}_{period}.png"
            filepath = os.path.join(self.chart_dir, filename)
            plt.savefig(filepath, dpi=DPI, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Chart saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Chart generation error for {ticker}: {e}")
            raise
    
    def plot_comparison_chart(
        self, 
        tickers: List[str], 
        period: str = "1y",
        normalize: bool = True
    ) -> str:
        """
        Generate comparison chart for multiple stocks.
        
        Shows price trends for multiple stocks on one chart.
        Optionally normalizes prices to percentage change for easier comparison.
        
        Args:
            tickers: List of ticker symbols to compare
            period: Time period
            normalize: If True, normalize to percentage change from start
        
        Returns:
            Path to saved chart image
        
        Example:
            >>> charts = ChartTools()
            >>> path = charts.plot_comparison_chart(
            ...     ["NVDA", "AMD", "INTC"], 
            ...     period="1y",
            ...     normalize=True
            ... )
        """
        try:
            logger.info(f"Generating comparison chart for {', '.join(tickers)}")
            
            fig, ax = plt.subplots(figsize=FIGSIZE)
            
            colors = ['#2E86DE', '#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181']
            
            for i, ticker in enumerate(tickers):
                stock = yf.Ticker(ticker)
                hist = stock.history(period=period)
                
                if hist.empty:
                    logger.warning(f"No data for {ticker}")
                    continue
                
                prices = hist['Close']
                
                if normalize:
                    # Normalize to percentage change
                    prices = (prices / prices.iloc[0] - 1) * 100
                    ylabel = 'Change (%)'
                else:
                    ylabel = 'Price (USD)'
                
                ax.plot(hist.index, prices, label=ticker.upper(), 
                       color=colors[i % len(colors)], linewidth=2)
            
            # Formatting
            title = f'Stock Comparison - {", ".join([t.upper() for t in tickers])} ({period})'
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.legend(loc='upper left')
            ax.grid(True, alpha=0.3)
            
            # Add zero line if normalized
            if normalize:
                ax.axhline(y=0, color='black', linestyle='--', alpha=0.3)
            
            # Format dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            plt.tight_layout()
            
            # Save
            filename = f"comparison_{'_'.join(tickers)}_{period}.png"
            filepath = os.path.join(self.chart_dir, filename)
            plt.savefig(filepath, dpi=DPI, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Comparison chart saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Comparison chart error: {e}")
            raise


# Convenience functions for direct use
def plot_stock(ticker: str, period: str = "1y") -> str:
    """Quick function to plot a stock chart."""
    charts = ChartTools()
    return charts.plot_stock_history(ticker, period=period)


def plot_comparison(tickers: List[str], period: str = "1y") -> str:
    """Quick function to plot comparison chart."""
    charts = ChartTools()
    return charts.plot_comparison_chart(tickers, period=period)
