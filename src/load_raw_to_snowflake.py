from pathlib import Path
import csv
import os
import re

import snowflake.connector
from dotenv import load_dotenv


RAW_DIR = Path("data/raw/csv")

CORE_FILES = [
    "patients.csv",
    "encounters.csv",
    "conditions.csv",
    "medications.csv",
    "procedures.csv",
    "observations.csv",
]


def clean_column_name(column_name):
    column_name = column_name.strip().upper()
    column_name = re.sub(r"[^A-Z0-9_]", "_", column_name)
    column_name = re.sub(r"_+", "_", column_name).strip("_")

    if not column_name:
        column_name = "COLUMN"

    if column_name[0].isdigit():
        column_name = f"COL_{column_name}"

    return column_name


def get_clean_columns(csv_path):
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        raw_columns = next(reader)

    clean_columns = []
    seen = {}

    for column in raw_columns:
        clean_col = clean_column_name(column)

        if clean_col in seen:
            seen[clean_col] += 1
            clean_col = f"{clean_col}_{seen[clean_col]}"
        else:
            seen[clean_col] = 1

        clean_columns.append(clean_col)

    return clean_columns


def quote_identifier(identifier):
    return f'"{identifier.replace(chr(34), chr(34) + chr(34))}"'


def create_raw_table(cursor, table_name, columns):
    column_sql = ",\n    ".join(
        f"{quote_identifier(column)} VARCHAR" for column in columns
    )

    create_sql = f"""
    CREATE OR REPLACE TABLE {table_name} (
        {column_sql}
    );
    """

    cursor.execute(create_sql)


def load_file(cursor, csv_path):
    table_name = csv_path.stem.upper()
    columns = get_clean_columns(csv_path)

    print(f"\nCreating RAW table: {table_name}")
    create_raw_table(cursor, table_name, columns)

    file_uri = csv_path.resolve().as_posix()

    print(f"Uploading file to Snowflake stage: {csv_path.name}")
    cursor.execute(
        f"""
        PUT 'file://{file_uri}'
        @CSV_STAGE
        AUTO_COMPRESS = TRUE
        OVERWRITE = TRUE;
        """
    )

    print(f"Copying staged file into RAW.{table_name}")
    cursor.execute(
        f"""
        COPY INTO {table_name}
        FROM @CSV_STAGE
        FILES = ('{csv_path.name}.gz')
        FILE_FORMAT = (FORMAT_NAME = CSV_FORMAT)
        ON_ERROR = 'ABORT_STATEMENT';
        """
    )

    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    row_count = cursor.fetchone()[0]

    print(f"Loaded {row_count} rows into RAW.{table_name}")


def main():
    load_dotenv()

    mfa_passcode = input("Enter your Snowflake MFA code: ").strip()

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        authenticator="username_password_mfa",
        passcode=mfa_passcode,
        role=os.environ.get("SNOWFLAKE_ROLE"),
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )

    cursor = conn.cursor()

    try:
        cursor.execute(f"USE WAREHOUSE {os.environ['SNOWFLAKE_WAREHOUSE']};")
        cursor.execute(f"USE DATABASE {os.environ['SNOWFLAKE_DATABASE']};")
        cursor.execute(f"USE SCHEMA {os.environ['SNOWFLAKE_SCHEMA']};")

        for file_name in CORE_FILES:
            csv_path = RAW_DIR / file_name

            if not csv_path.exists():
                print(f"Skipping missing file: {csv_path}")
                continue

            load_file(cursor, csv_path)

        print("\nRAW load complete.")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()