import json
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# HTML template using TradingView's Lightweight Charts
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coinbase Market Data Visualization</title>
    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #131722;
            color: #d1d4dc;
            margin: 0;
            padding: 20px;
        }
        h1 {
            text-align: center;
            font-weight: 300;
            margin-bottom: 30px;
        }
        .charts-container {
            display: flex;
            flex-direction: column;
            gap: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .chart-box {
            background-color: #1e222d;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .chart-title {
            font-size: 24px;
            font-weight: 600;
        }
        .chart-container {
            position: relative;
            width: 100%;
            height: 400px;
        }
    </style>
</head>
<body>
    <h1>Historical Market Data (Last 3 Hours)</h1>
    
    <div class="charts-container" id="charts">
        <!-- Charts will be injected here by JavaScript -->
    </div>

    <script>
        // Fetch the data from our API endpoint
        fetch('/api/data')
            .then(response => response.json())
            .then(marketData => {
                const container = document.getElementById('charts');
                
                // Iterate over each asset (BTC-USD, ETH-USD)
                for (const [asset, data] of Object.entries(marketData)) {
                    
                    // 1. Create HTML elements for this chart
                    const chartBox = document.createElement('div');
                    chartBox.className = 'chart-box';
                    
                    const header = document.createElement('div');
                    header.className = 'chart-header';
                    header.innerHTML = `<div class="chart-title">${asset}</div>`;
                    
                    const chartDiv = document.createElement('div');
                    chartDiv.className = 'chart-container';
                    chartDiv.id = `chart-${asset}`;
                    
                    chartBox.appendChild(header);
                    chartBox.appendChild(chartDiv);
                    container.appendChild(chartBox);
                    
                    // 2. Format the data for Lightweight Charts
                    // Lightweight charts requires { time, open, high, low, close }
                    const candlestickData = data.map(candle => {
                        // Convert "YYYY-MM-DD HH:MM:SS" to a unix timestamp (seconds)
                        const timestamp = new Date(candle.timestamp + "Z").getTime() / 1000;
                        return {
                            time: timestamp,
                            open: candle.open,
                            high: candle.high,
                            low: candle.low,
                            close: candle.close
                        };
                    });
                    
                    // 3. Initialize the chart
                    const chart = LightweightCharts.createChart(chartDiv, {
                        layout: {
                            background: { type: 'solid', color: '#1e222d' },
                            textColor: '#d1d4dc',
                        },
                        grid: {
                            vertLines: { color: '#2b2b43' },
                            horzLines: { color: '#2b2b43' },
                        },
                        crosshair: {
                            mode: LightweightCharts.CrosshairMode.Normal,
                        },
                        rightPriceScale: {
                            borderColor: '#2b2b43',
                        },
                        timeScale: {
                            borderColor: '#2b2b43',
                            timeVisible: true,
                            secondsVisible: false,
                        },
                    });
                    
                    // 4. Add the Candlestick series
                    const candlestickSeries = chart.addCandlestickSeries({
                        upColor: '#26a69a',
                        downColor: '#ef5350',
                        borderVisible: false,
                        wickUpColor: '#26a69a',
                        wickDownColor: '#ef5350',
                    });
                    
                    // 5. Set the data
                    candlestickSeries.setData(candlestickData);
                    
                    // Make the chart fit the data nicely
                    chart.timeScale().fitContent();
                    
                    // Handle window resizing
                    window.addEventListener('resize', () => {
                        chart.applyOptions({ width: chartDiv.clientWidth });
                    });
                }
            })
            .catch(error => console.error("Error loading market data:", error));
    </script>
</body>
</html>
"""

@app.get("/")
def get_ui():
    """Serves the main HTML page."""
    return HTMLResponse(html_template)

@app.get("/api/data")
def get_data():
    """API endpoint that returns the JSON data."""
    file_path = "coinbase_market_data.json"
    if not os.path.exists(file_path):
        return {"error": "Data file not found. Please run fetch_market_data.py first."}
        
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    print("Starting Visualization Server...")
    print("Open your browser and navigate to: http://127.0.0.1:8002")
    uvicorn.run(app, host="127.0.0.1", port=8002)
