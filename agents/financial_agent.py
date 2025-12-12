from langchain.tools import BaseTool, tool
from agents.base_agent import BaseAgent
from tools.financial_tools import FinancialTools
from config.settings import settings
import json

# Create tool functions with proper decorators
@tool
def get_stock_data_tool(ticker: str) -> str:
    """Get current stock price and basic information"""
    try:
        data = FinancialTools.get_stock_data(ticker)
        if "error" in data:
            return f"Error getting stock data for {ticker}: {data['error']}"
        
        formatted = f"## Stock Data for {ticker.upper()}:\n"
        formatted += f"- **Current Price**: ${data.get('current_price', 'N/A')} {data.get('currency', '')}\n"
        formatted += f"- **Open**: ${data.get('open', 'N/A')}\n"
        formatted += f"- **High**: ${data.get('high', 'N/A')}\n"
        formatted += f"- **Low**: ${data.get('low', 'N/A')}\n"
        formatted += f"- **Close**: ${data.get('close', 'N/A')}\n"
        formatted += f"- **Volume**: {data.get('volume', 'N/A'):,}\n"
        formatted += f"- **Market Cap**: ${data.get('market_cap', 'N/A'):,}\n"
        formatted += f"- **P/E Ratio**: {data.get('pe_ratio', 'N/A')}\n"
        return formatted
    except Exception as e:
        return f"Error getting stock data: {str(e)}"

@tool
def get_analyst_recommendations_tool(ticker: str) -> str:
    """Get analyst recommendations and price targets"""
    try:
        data = FinancialTools.get_analyst_recommendations(ticker)
        if "error" in data:
            return f"Error getting analyst recommendations for {ticker}: {data['error']}"
        
        formatted = f"## Analyst Recommendations for {ticker.upper()}:\n"
        formatted += f"- **Recommendation**: {data.get('recommendation', 'N/A')}\n"
        formatted += f"- **Mean Recommendation**: {data.get('mean_recommendation', 'N/A')}\n"
        formatted += f"- **Number of Analysts**: {data.get('num_analysts', 'N/A')}\n"
        formatted += f"- **Target Mean Price**: ${data.get('target_mean', 'N/A')}\n"
        formatted += f"- **Target High Price**: ${data.get('target_high', 'N/A')}\n"
        formatted += f"- **Target Low Price**: ${data.get('target_low', 'N/A')}\n"
        return formatted
    except Exception as e:
        return f"Error getting analyst recommendations: {str(e)}"

@tool
def get_company_news_tool(ticker: str) -> str:
    """Get latest company news and updates"""
    try:
        news_items = FinancialTools.get_company_news(ticker)
        if not news_items or (len(news_items) == 1 and "error" in news_items[0]):
            return f"No recent news found for {ticker}."
        
        formatted = f"## Recent News for {ticker.upper()}:\n"
        for i, item in enumerate(news_items[:3], 1):
            formatted += f"\n{i}. **{item.get('title', 'No title')}**\n"
            formatted += f"   Publisher: {item.get('publisher', 'Unknown')}\n"
            if item.get('published'):
                formatted += f"   Published: {item.get('published')}\n"
        return formatted
    except Exception as e:
        return f"Error getting company news: {str(e)}"

@tool
def get_fundamentals_tool(ticker: str) -> str:
    """Get company fundamentals and financial ratios"""
    try:
        data = FinancialTools.get_fundamentals(ticker)
        if "error" in data:
            return f"Error getting fundamentals for {ticker}: {data['error']}"
        
        formatted = f"## Fundamentals for {ticker.upper()}:\n"
        formatted += f"- **Market Cap**: ${data.get('market_cap', 'N/A'):,}\n"
        formatted += f"- **P/E Ratio**: {data.get('pe_ratio', 'N/A')}\n"
        formatted += f"- **Forward P/E**: {data.get('forward_pe', 'N/A')}\n"
        formatted += f"- **PEG Ratio**: {data.get('peg_ratio', 'N/A')}\n"
        formatted += f"- **Price to Book**: {data.get('price_to_book', 'N/A')}\n"
        formatted += f"- **Debt to Equity**: {data.get('debt_to_equity', 'N/A')}\n"
        formatted += f"- **Return on Equity**: {data.get('return_on_equity', 'N/A')}\n"
        formatted += f"- **Profit Margins**: {data.get('profit_margins', 'N/A')}\n"
        formatted += f"- **Revenue Growth**: {data.get('revenue_growth', 'N/A')}\n"
        return formatted
    except Exception as e:
        return f"Error getting fundamentals: {str(e)}"

class FinancialAgent(BaseAgent):
    """Financial data agent for stock and market information"""
    
    def __init__(self):
        # Create financial tools using the new tool decorator
        tools = [
            get_stock_data_tool,
            get_analyst_recommendations_tool,
            get_company_news_tool,
            get_fundamentals_tool
        ]
        
        # Define agent role
        role = (
            "A senior quantitative financial analyst specializing in real-time and "
            "historical market data analysis. You retrieve, analyze, and interpret "
            "financial information to support investment research."
        )
        
        super().__init__(
            name="Financial Data Agent",
            role=role,
            tools=tools,
            model_name=settings.PRIMARY_MODEL
        )