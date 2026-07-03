# Cambia Health Data Pipeline

End-to-end healthcare data engineering project using synthetic Synthea patient data.

## Project Goal

Build a healthcare data pipeline that validates raw CSV data, loads it into Snowflake, transforms it into analytics-ready tables, and powers a dashboard and future data access copilot.

## Pipeline

Synthea CSV data  
Python + Pandas validation  
Snowflake RAW schema  
Snowflake STAGING schema  
Kimball STAR schema  
Streamlit dashboard  
RAG Data Access Copilot  

## Current Progress

- Created Python virtual environment
- Installed Pandas, NumPy, and PyArrow
- Downloaded Synthea CSV dataset
- Validated CSV files using Python
- Generated data quality report

## Current Artifact

- `outputs/data_quality_report.csv`

## Tech Stack

- Python
- Pandas
- Snowflake
- SQL
- Streamlit
- GitHub