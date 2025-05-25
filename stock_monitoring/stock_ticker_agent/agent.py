import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from typing import Dict, List, Any
import requests
from newsapi import NewsApiClient
from datetime import datetime, timedelta
import yfinance as yf

# Load environment variables
load_dotenv()

# Constants
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash-exp"
APP_NAME = "stock_analysis_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# API clients setup
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def identify_ticker(query: str) -> Dict[str, Any]:
    """
    Identifies stock ticker from company name using yfinance search.
    Falls back to Alpha Vantage Symbol Search if needed.
    """
    try:
        # Clean up the query to extract company name
        query = query.lower().replace("stock", "").strip()
        
        # Try yfinance search first
        tickers = yf.Tickers(query)
        if hasattr(tickers, 'tickers'):
            for symbol, ticker_obj in tickers.tickers.items():
                try:
                    info = ticker_obj.info
                    if info and 'longName' in info:
                        return {
                            "status": "success",
                            "data": {
                                "ticker": symbol,
                                "company_name": info['longName']
                            }
                        }
                except:
                    continue
        
        # If yfinance doesn't find it, try Alpha Vantage as backup
        search_url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(search_url)
        data = response.json()
        
        if "bestMatches" in data and len(data["bestMatches"]) > 0:
            match = data["bestMatches"][0]
            return {
                "status": "success",
                "data": {
                    "ticker": match["1. symbol"],
                    "company_name": match["2. name"]
                }
            }
        
        return {
            "status": "error",
            "error_message": "Could not find matching ticker symbol"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error in ticker identification: {str(e)}"
        }

def ticker_news(ticker: str) -> Dict[str, Any]:
    """
    Retrieves recent news about the stock using NewsAPI.
    """
    try:
        news = newsapi.get_everything(
            q=f"{ticker} stock",
            language='en',
            sort_by='publishedAt',
            page_size=5
        )
        return {
            "status": "success",
            "data": news['articles']
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error fetching news: {str(e)}"
        }

def ticker_price(ticker: str) -> Dict[str, Any]:
    """
    Fetches current stock price using Alpha Vantage Global Quote.
    """
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if "Global Quote" in data:
            quote = data["Global Quote"]
            return {
                "status": "success",
                "data": {
                    "price": float(quote["05. price"]),
                    "volume": int(quote["06. volume"]),
                    "trading_day": quote["07. latest trading day"],
                    "previous_close": float(quote["08. previous close"])
                }
            }
        return {
            "status": "error",
            "error_message": "No price data available"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error fetching price: {str(e)}"
        }

def ticker_price_change(ticker: str, timeframe: str = "today") -> Dict[str, Any]:
    """
    Calculates price change over given timeframe using Alpha Vantage Time Series Daily.
    """
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            dates = list(time_series.keys())
            
            if timeframe == "today":
                start_date = dates[1]  # Yesterday
                end_date = dates[0]    # Today
            elif timeframe == "week":
                start_date = dates[min(7, len(dates)-1)]
                end_date = dates[0]
            else:  # month
                start_date = dates[min(30, len(dates)-1)]
                end_date = dates[0]
            
            start_price = float(time_series[start_date]["4. close"])
            end_price = float(time_series[end_date]["4. close"])
            change = ((end_price - start_price) / start_price) * 100
            
            return {
                "status": "success",
                "data": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "start_price": start_price,
                    "end_price": end_price,
                    "percent_change": change,
                    "timeframe": timeframe
                }
            }
        return {
            "status": "error",
            "error_message": "No historical data available"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error calculating price change: {str(e)}"
        }

def ticker_analysis(ticker: str, news_data: Dict[str, Any], price_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes and summarizes stock performance using news and price data.
    """
    try:
        analysis = []
        
        # Price analysis
        if price_data["status"] == "success":
            price_info = price_data["data"]
            change = price_info["percent_change"]
            timeframe = price_info["timeframe"]
            
            if change > 0:
                analysis.append(f"The stock has increased by {abs(change):.2f}% over {timeframe}.")
            else:
                analysis.append(f"The stock has decreased by {abs(change):.2f}% over {timeframe}.")
        
        # News analysis
        if news_data["status"] == "success" and len(news_data["data"]) > 0:
            analysis.append("\nRecent news that might explain the movement:")
            for article in news_data["data"][:3]:
                analysis.append(f"- {article['title']}")
        
        return {
            "status": "success",
            "data": {
                "analysis": "\n".join(analysis)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error in analysis: {str(e)}"
        }

# Create the stock analysis agent
root_agent = Agent(
    name="stock_ticker_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="A comprehensive stock analysis agent that analyzes stocks using multiple data sources.",
    instruction="""You are a sophisticated stock market analyst. When users ask about stocks:
    1. Use identify_ticker to find the correct stock symbol
    2. Use ticker_price to get current price data
    3. Use ticker_price_change to analyze price movements
    4. Use ticker_news to gather recent news
    5. Use ticker_analysis to provide comprehensive insights
    
    Handle queries like:
    - "Why did Tesla stock drop today?"
    - "What's happening with Palantir stock recently?"
    - "How has Nvidia stock changed in the last 7 days?"
    
    Always provide context and explain the reasons behind stock movements using both price data and news.
    """,
    tools=[
        identify_ticker,
        ticker_news,
        ticker_price,
        ticker_price_change,
        ticker_analysis
    ]
)