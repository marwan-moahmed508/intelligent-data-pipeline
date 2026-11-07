# Intelligent Data Pipeline

An end-to-end Data Engineering project that collects remote job data from a public API, transforms and validates the data, and loads it into PostgreSQL using a modular ETL pipeline.

## Project Overview

The **Intelligent Data Pipeline** automates the process of collecting and processing remote job listings.

The pipeline extracts job data from the Remotive API, cleans and transforms the raw records, performs data quality checks, and stores the results in a PostgreSQL database.

The project demonstrates practical Data Engineering concepts, including API integration, data transformation, validation, relational database management, and idempotent data loading.

## Architecture

```text
Remotive API
     |
     v
  Extraction
     |
     v
  Raw JSON Data
     |
     v
 Transformation
     |
     v
  Cleaned CSV
     |
     v
 Data Validation
     |
     v
  PostgreSQL
```

## Technologies Used

- **Python** – Main programming language.
- **Requests** – API integration and data extraction.
- **Pandas** – Data cleaning and transformation.
- **BeautifulSoup4** – HTML content cleaning.
- **PostgreSQL** – Relational database storage.
- **SQLAlchemy** – Database connectivity and operations.
- **Pytest** – Testing framework.
- **Git & GitHub** – Version control.

## Project Structure

```text
intelligent-data-pipeline/
│
├── dags/
├── data/
│   ├── raw/
│   └── processed/
│
├── docker/
│
├── sql/
│   └── schema.sql
│
├── src/
│   ├── ingestion/
│   │   └── fetch_jobs.py
│   │
│   ├── transformation/
│   │   └── clean_jobs.py
│   │
│   ├── validation/
│   │   └── quality_checks.py
│   │
│   └── database/
│       ├── postgres.py
│       └── load_jobs.py
│
├── tests/
├── main.py
├── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## ETL Workflow

### 1. Extraction
- Connects to the Remotive public API.
- Retrieves remote job listings.
- Saves the raw API response as a timestamped JSON file.

### 2. Transformation
- Removes HTML tags from job descriptions.
- Selects relevant job attributes.
- Handles missing values.
- Removes duplicate job records.
- Normalizes tags and publication dates.
- Saves the cleaned data as a CSV file.

### 3. Data Validation
- Checks whether the dataset contains records.
- Identifies duplicate job IDs.
- Checks for missing required fields.
- Validates URLs and publication dates.
- Stops the pipeline if critical validation checks fail.

### 4. Loading
- Loads cleaned records into PostgreSQL.
- Uses an UPSERT operation to handle existing records.
- Updates existing records instead of inserting duplicates.

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/marwan-moahmed508/intelligent-data-pipeline.git
cd intelligent-data-pipeline
```

### 2. Create a virtual environment

Windows:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=remote_jobs_db
DB_USER=postgres
DB_PASSWORD=your_password
```

Replace `your_password` with your PostgreSQL password.

**Important:** Never commit your `.env` file or database credentials to GitHub.

### 5. Configure PostgreSQL

Create a database named:

```sql
CREATE DATABASE remote_jobs_db;
```

Then execute the SQL statements in `sql/schema.sql` to create the required table.

Make sure PostgreSQL is running before executing the pipeline.

## Running the Pipeline

Run the complete ETL pipeline from the project root:

```bash
python main.py
```

The pipeline will automatically:

1. Fetch remote job listings.
2. Save the raw JSON response.
3. Transform and clean the data.
4. Run data quality checks.
5. Load the validated records into PostgreSQL.

## Key Features

- Modular ETL architecture.
- REST API integration.
- Automated data cleaning and validation.
- PostgreSQL integration.
- Idempotent data loading using UPSERT.
- Environment-based database configuration.
- Logging and error handling.
- Timestamped raw and processed data files.

## Future Improvements

- Integrate Apache Airflow for workflow orchestration and scheduling.
- Containerize the project using Docker.
- Add automated unit and integration tests.
- Increase API extraction coverage after reviewing API limits.
- Add machine learning capabilities for job classification and skill extraction.
- Build analytical dashboards and reporting features.

## Data Source

Job listings are retrieved from the [Remotive API](https://remotive.com/api/remote-jobs).

This project is intended for educational and analytical purposes. Original job listing links are preserved to direct users to the source.

## Author

**Marwan Mohammed**

- GitHub: [marwan-moahmed508](https://github.com/marwan-moahmed508)
- LinkedIn: [Marwan Mohammed](https://www.linkedin.com/in/marwan-mohammed-854b23336/)
- Portfolio: [Personal Portfolio](https://marwan-moahmed508.github.io/Marwan-Portfolio/)

---

*Built as a practical Data Engineering project, with plans to expand into Machine Learning, Generative AI, and intelligent automation.*