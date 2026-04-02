# E Commerce Analysis Dashboard

## Requirements

- Python 3.8+
- pip

## Installation

Install the required dependencies:

```bash
pip install streamlit pandas matplotlib seaborn
```

## Project Structure

```
dashboard.py
Analysis Data Project.ipynb (Notebook)
requirements.txt
dataset/
  olist_orders_dataset.csv
  olist_order_payments_dataset.csv
  olist_order_items_dataset.csv
  olist_customers_dataset.csv
  olist_sellers_dataset.csv
  olist_order_reviews_dataset.csv
  olist_products_dataset.csv
  olist_geolocation_dataset.csv
  product_category_name_translation.csv
```

Make sure the `dataset/` folder is in the same directory as `dashboard.py`.

## Running the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`.

If it does not open automatically, open your browser and navigate to that URL manually.

## Stopping the Dashboard

Press `Ctrl+C` in the terminal.

## Features

- **Filter by date** — use the date picker in the sidebar to filter data by date range
- **Dashboard page** — KPI metrics, order volume by hour, heatmap of orders by day and hour, payment method analysis
- **Insight page** — written analysis and conclusions from the visualizations (Indonesian)
