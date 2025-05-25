# Stock Ticker Agent using Google ADK

A sophisticated multi-agent system built with Google ADK that analyzes stocks using natural language queries. The system combines data from multiple sources including Alpha Vantage for stock data and NewsAPI for recent news.

## Features

### Tools (Subagents)

1. `identify_ticker`: Dynamically converts company names to stock tickers using yfinance

   - Example: "Tesla" → "TSLA"
   - Uses yfinance for primary lookup
   - Falls back to Alpha Vantage Symbol Search

2. `ticker_news`: Fetches recent news about stocks

   - Uses NewsAPI
   - Returns top 5 most recent articles
   - Includes titles and descriptions

3. `ticker_price`: Gets real-time stock prices

   - Uses Alpha Vantage Global Quote
   - Includes current price, volume, and previous close

4. `ticker_price_change`: Analyzes price changes over time

   - Supports different timeframes (today, week, month)
   - Uses Alpha Vantage Time Series Daily
   - Calculates percentage changes

5. `ticker_analysis`: Provides comprehensive analysis
   - Combines price movements and news
   - Explains potential reasons for stock movements
   - Summarizes key information

## Prerequisites

- Python 3.8 or higher
- Google ADK access
- API Keys:
  - Alpha Vantage API key (get it from [Alpha Vantage](https://www.alphavantage.co/support/#api-key))
  - News API key (get it from [NewsAPI](https://newsapi.org/register))

## Setup Instructions

1. Clone the repository:

```bash
git clone <repository-url>
cd sp-google-adk
```

2. Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
source venv/Scripts/activate

# Unix/MacOS
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```env
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
NEWS_API_KEY=your_news_api_key_here
```

## Running the Agent

Start the web interface:

```bash
adk web
```

Then open your browser and navigate to:

```
http://localhost:8000
```

## Example Queries

Try these example queries in the web interface:

- "Why did Tesla stock drop today?"
- "What's happening with Palantir stock recently?"
- "How has Nvidia stock changed in the last 7 days?"

## How It Works

### Tool Implementation

Each tool is implemented as a function that:

1. Takes specific inputs (e.g., ticker symbol, timeframe)
2. Makes API calls to relevant services
3. Returns standardized responses:

```python
{
    "status": "success|error",
    "data": {
        # Tool-specific data
    }
    # OR
    "error_message": "Error description"
}
```

### Data Sources

- **Stock Data**:

  - Primary: yfinance for symbol lookup
  - Secondary: Alpha Vantage for detailed data
  - Endpoints used:
    - Global Quote
    - Time Series Daily
    - Symbol Search

- **News Data**:
  - NewsAPI for recent articles
  - Filtered by relevance and recency
  - Limited to English language sources

### Error Handling

- All tools include comprehensive error handling
- Fallback mechanisms for ticker identification
- Clear error messages for debugging

## Troubleshooting

1. **API Rate Limits**:

   - Alpha Vantage: 5 calls per minute for free tier
   - NewsAPI: 100 calls per day for free tier
   - Consider upgrading for production use

2. **Common Issues**:
   - If ticker identification fails, try using the exact stock symbol
   - Check your API keys if you get authentication errors
   - Ensure your .env file is in the correct location

## Contributing

Feel free to submit issues and enhancement requests!
