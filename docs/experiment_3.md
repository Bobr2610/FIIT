Below is an updated version of the previous HTML with integrated CSS. I've added a mockup pie chart and trend graph for three mock companies: "AlphaCorp," "BetaTech," and "GammaSolutions." The charts are created using basic `<div>` elements styled with CSS for simplicity.

### Updated `index.html` with Integrated CSS
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Currency Exchange and Analytics</title>
    <style>
        /* Basic CSS Reset */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f8f8;
        }

        header {
            background-color: #333;
            color: white;
            padding: 1rem;
            text-align: center;
        }

        header h1 {
            font-size: 2rem;
        }

        .table-container {
            max-width: 800px;
            margin: 2rem auto;
            background-color: #fff;
            padding: 1rem;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            border-radius: 4px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 0.75rem;
            text-align: center;
            border: 1px solid #ddd;
        }

        th {
            background-color: #333;
            color: white;
        }

        tbody tr:nth-child(even) {
            background-color: #f3f3f3;
        }

        /* Pie Chart Style */
        .pie-chart-container {
            max-width: 800px;
            margin: 2rem auto;
            text-align: center;
        }

        .pie-chart {
            width: 200px;
            height: 200px;
            background: conic-gradient(
                #4caf50 0% 40%, 
                #ff9800 40% 70%, 
                #f44336 70% 100%
            );
            border-radius: 50%;
            margin: 0 auto;
        }

        /* Trend Graph Style */
        .trend-graph-container {
            max-width: 800px;
            margin: 2rem auto;
            text-align: center;
        }

        .trend-graph {
            width: 100%;
            height: 200px;
            background: linear-gradient(90deg, #4caf50 25%, #ff9800 50%, #f44336 75%);
            position: relative;
        }

        .trend-graph span {
            position: absolute;
            top: 10px;
            left: 25%;
            font-size: 0.8rem;
            color: white;
        }

        footer {
            text-align: center;
            padding: 1rem;
            background-color: #333;
            color: white;
        }
    </style>
</head>
<body>
    <header>
        <h1>Currency Exchange and Analytics</h1>
    </header>
    <main>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Currency Pair</th>
                        <th>Last Price</th>
                        <th>Previous Price</th>
                    </tr>
                </thead>
                <tbody id="rates-table">
                    <!-- Example rows -->
                    <tr>
                        <td>USD/RUB</td>
                        <td>80.25</td>
                        <td>79.80</td>
                    </tr>
                    <tr>
                        <td>EUR/RUB</td>
                        <td>85.50</td>
                        <td>84.90</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="pie-chart-container">
            <h2>Market Share (Mock Data)</h2>
            <div class="pie-chart"></div>
            <p>AlphaCorp: 40%, BetaTech: 30%, GammaSolutions: 30%</p>
        </div>

        <div class="trend-graph-container">
            <h2>Performance Trend (Mock Data)</h2>
            <div class="trend-graph">
                <span>AlphaCorp</span>
            </div>
        </div>
    </main>
    <footer>
        <p>&copy; 2025 Currency Exchange and Analytics</p>
    </footer>
</body>
</html>
```

### Explanation
1. **Pie Chart:**
   - The pie chart uses the `conic-gradient` CSS feature for simplicity.
   - The three colors represent AlphaCorp (40%), BetaTech (30%), and GammaSolutions (30%).
   - Adjust the percentages and colors to reflect real data if needed.

2. **Trend Graph:**
   - The trend graph uses a `linear-gradient` with three distinct color segments.
   - Each segment represents the performance of one company.
   - You can add real data with JavaScript or use SVG/Canvas for more detailed graphs.

This structure keeps everything lightweight, flat, and easy to integrate. Let me know if you'd like to add dynamic functionality for live data updates!