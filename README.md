# Olist Brazilian E-Commerce Data Pipeline

An end-to-end Data Engineering project built around the Brazilian E-Commerce Public Dataset by Olist.

The project processes raw e-commerce data, performs data cleaning and transformation, loads the results into PostgreSQL, and provides analytical SQL views and an interactive Streamlit dashboard.

## Project Overview

This project demonstrates a practical data engineering workflow using real-world e-commerce data.

The pipeline covers:
- Reading and processing multiple CSV datasets.
- Cleaning and transforming raw data with Pandas.
- Loading structured data into PostgreSQL.
- Building SQL views for business analytics.
- Exploring business KPIs through an interactive dashboard.
- Testing pipeline components with Pytest.

## Architecture

```text
Olist Raw CSV Files
        |
        v
Data Ingestion
        |
        v
Data Cleaning & Transformation
        |
        v
Processed CSV Files
        |
        v
PostgreSQL Database
        |
        v
Analytical SQL Views
        |
        v
Streamlit Dashboard
```

## Dataset

The project uses the Brazilian E-Commerce Public Dataset by Olist.

It contains information about customers, orders, products, sellers, payments, reviews, geolocation, and product categories.

The pipeline uses nine CSV datasets:

- olist_customers_dataset.csv
- olist_geolocation_dataset.csv
- olist_order_items_dataset.csv
- olist_order_payments_dataset.csv
- olist_order_reviews_dataset.csv
- olist_orders_dataset.csv
- olist_products_dataset.csv
- olist_sellers_dataset.csv
- product_category_name_translation.csv

Place the downloaded CSV files in:

```text
data/raw/olist/
```

## Technologies

- Python
- Pandas
- PostgreSQL
- SQLAlchemy
- Psycopg2
- Streamlit
- Plotly
- Pytest
- Git & GitHub

## Project Structure

```text
intelligent-data-pipeline/
|
├── data/
│   ├── raw/
│   │   └── olist/
│   └── processed/
|
├── dashboard/
│   └── olist_app.py
|
├── scripts/
|
├── sql/
│   ├── olist_schema.sql
│   ├── olist_analytics_views.sql
│   └── olist_category_analytics.sql
|
├── src/
│   ├── ingestion/
│   │   └── read_olist.py
│   ├── transformation/
│   │   └── clean_olist.py
│   └── database/
│       ├── postgres.py
│       └── load_olist.py
|
├── tests/
│   └── test_olist_pipeline.py
|
├── .streamlit/
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/marwan-moahmed508/intelligent-data-pipeline.git
cd intelligent-data-pipeline
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
OLIST_DB_NAME=olist_ecommerce_db
```

Replace `your_password` with your local PostgreSQL password.

Never commit `.env` or database credentials to version control.

### 5. Prepare PostgreSQL

Create the database:

```sql
CREATE DATABASE olist_ecommerce_db;
```

Apply the database schema:

```powershell
psql -U postgres -d olist_ecommerce_db -f sql/olist_schema.sql
```

Make sure PostgreSQL is running before continuing.

### 6. Run the pipeline

After placing the nine raw CSV files in `data/raw/olist/`, run:

```powershell
python main.py
```

The pipeline transforms the raw datasets and loads the resulting data into PostgreSQL.

The database loader expects the target tables to be empty before loading.

### 7. Create analytical views

After loading the data, execute:

```powershell
psql -U postgres -d olist_ecommerce_db -f sql/olist_analytics_views.sql
psql -U postgres -d olist_ecommerce_db -f sql/olist_category_analytics.sql
```

## Run the Dashboard

Start the Streamlit dashboard:

```powershell
python -m streamlit run dashboard/olist_app.py
```

The dashboard provides an interactive overview of e-commerce performance, including:

- Order and sales KPIs.
- Monthly sales trends.
- Order status distribution.
- Product and category performance.
- Customer analytics.
- Data quality indicators.

## Run Tests

Execute the test suite:

```powershell
python -m pytest tests -v
```

## Database

The PostgreSQL database used by the project is:

```text
olist_ecommerce_db
```

It contains the nine Olist source tables and analytical SQL views.

## Author

**Marwan Mohammed**

- GitHub: [marwan-moahmed508](https://github.com/marwan-moahmed508)
- LinkedIn: [Marwan Mohammed](https://www.linkedin.com/in/marwan-mohammed-854b23336/)
- Portfolio: [Personal Portfolio](https://marwan-moahmed508.github.io/Marwan-Portfolio/)