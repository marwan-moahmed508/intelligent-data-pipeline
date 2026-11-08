# Olist Brazilian E-Commerce Data Pipeline

An end-to-end Data Engineering project built around the Brazilian E-Commerce Public Dataset by Olist.

This project demonstrates a complete data pipeline that ingests raw e-commerce data, cleans and transforms it using Python and Pandas, loads it into PostgreSQL, and delivers business insights through analytical SQL views and an interactive Streamlit dashboard.

## Project Overview

The project processes real-world Brazilian e-commerce data and transforms it into structured, analytics-ready datasets.

The pipeline covers:

- Reading nine raw CSV datasets.
- Cleaning and transforming data with Pandas.
- Performing data quality checks and handling date and numeric fields.
- Loading processed datasets into PostgreSQL.
- Creating analytical SQL views.
- Exploring business KPIs through an interactive Streamlit dashboard.
- Testing data pipeline components with Pytest.

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

This project uses the **Brazilian E-Commerce Public Dataset by Olist**, a real-world dataset containing approximately 100,000 orders made between 2016 and 2018.

**Dataset source:** [Brazilian E-Commerce Public Dataset by Olist – Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

The dataset contains information about:

- Customers and customer locations.
- Orders and order status.
- Products and product categories.
- Sellers.
- Payments.
- Customer reviews.
- Geolocation data.

### Required CSV Files

The pipeline uses the following nine CSV files:

1. `olist_customers_dataset.csv`
2. `olist_geolocation_dataset.csv`
3. `olist_order_items_dataset.csv`
4. `olist_order_payments_dataset.csv`
5. `olist_order_reviews_dataset.csv`
6. `olist_orders_dataset.csv`
7. `olist_products_dataset.csv`
8. `olist_sellers_dataset.csv`
9. `product_category_name_translation.csv`

### Data Setup

1. Download the dataset from the Kaggle link above.
2. Extract the downloaded archive.
3. Create the following directory if it does not already exist:

```text
data/raw/olist/
```

4. Place all nine CSV files inside that directory.

**Important:** Raw and processed dataset files are excluded from this GitHub repository through `.gitignore` because of their size. You must download the dataset and place the files locally before running the pipeline.

## Technologies

- Python 3.13
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
├── .streamlit/
│   └── config.toml
|
├── dashboard/
│   └── olist_app.py
|
├── data/
│   ├── raw/
│   │   └── olist/
│   └── processed/
│       └── olist/
|
├── scripts/
│   ├── export_date_anomalies.py
│   ├── inspect_anomalies.py
│   ├── inspect_olist.py
│   └── validate_olist.py
|
├── sql/
│   ├── olist_schema.sql
│   ├── olist_analytics_views.sql
│   └── olist_category_analytics.sql
|
├── src/
│   ├── ingestion/
│   │   └── read_olist.py
│   │
│   ├── transformation/
│   │   └── clean_olist.py
│   │
│   └── database/
│       ├── postgres.py
│       └── load_olist.py
|
├── tests/
│   └── test_olist_pipeline.py
|
├── main.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Setup

### 1. Clone the Repository

```powershell
git clone https://github.com/marwan-moahmed508/intelligent-data-pipeline.git

cd intelligent-data-pipeline
```

### 2. Create and Activate a Virtual Environment

Windows PowerShell:

```powershell
py -3.13 -m venv .venv

.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
OLIST_DB_NAME=olist_ecommerce_db
```

Replace `your_password` with your local PostgreSQL password.

**Security:** Never commit `.env` or database credentials to version control.

### 5. Prepare PostgreSQL

Make sure PostgreSQL is installed and running.

Create the project database:

```sql
CREATE DATABASE olist_ecommerce_db;
```

Apply the database schema:

```powershell
psql -U postgres -d olist_ecommerce_db -f sql/olist_schema.sql
```

The database schema must be created before running the pipeline.

### 6. Run the Data Pipeline

After placing all nine raw CSV files in `data/raw/olist/`, execute:

```powershell
python main.py
```

The pipeline performs the following operations:

1. Reads the raw Olist datasets.
2. Cleans and transforms the data.
3. Saves processed CSV files.
4. Loads the processed datasets into PostgreSQL.

**Important:** The database loader expects the target tables to be empty before loading. Do not run the loading pipeline again against already populated tables without preparing an appropriate reload procedure.

### 7. Create Analytical SQL Views

After the data has been successfully loaded, execute:

```powershell
psql -U postgres -d olist_ecommerce_db -f sql/olist_analytics_views.sql

psql -U postgres -d olist_ecommerce_db -f sql/olist_category_analytics.sql
```

These SQL scripts create analytical views for business reporting and dashboard analysis.

## Run the Dashboard

Start the interactive Streamlit dashboard:

```powershell
python -m streamlit run dashboard/olist_app.py
```

The dashboard provides an interactive overview of e-commerce performance, including:

- Order and sales KPIs.
- Monthly sales trends.
- Order status distribution.
- Product performance.
- Category performance.
- Customer analytics.
- Data quality indicators.

## Data Quality & Validation

The project includes data validation and inspection scripts:

- `inspect_olist.py` – Inspects Olist datasets.
- `validate_olist.py` – Performs dataset validation.
- `inspect_anomalies.py` – Inspects detected date anomalies.
- `export_date_anomalies.py` – Exports date anomaly reports.

## Run Tests

Execute the test suite:

```powershell
python -m pytest tests -v
```

The tests cover:

- Processed and raw row-count consistency.
- Primary key uniqueness.
- Composite key uniqueness.
- Referential integrity between datasets.
- Order date quality flags.
- Product category translation.

## Database

The PostgreSQL database used by this project is:

```text
olist_ecommerce_db
```

It contains nine Olist source tables and analytical SQL views for business intelligence and reporting.

## Author

**Marwan Mohammed**

- GitHub: [marwan-moahmed508](https://github.com/marwan-moahmed508)
- LinkedIn: [Marwan Mohammed](https://www.linkedin.com/in/marwan-mohammed-854b23336/)
- Portfolio: [Personal Portfolio](https://marwan-moahmed508.github.io/Marwan-Portfolio/)