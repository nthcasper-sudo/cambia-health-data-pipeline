from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw/csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


CORE_FILES = {
    "patients.csv": ["Id", "BIRTHDATE", "GENDER", "CITY", "STATE", "HEALTHCARE_EXPENSES", "HEALTHCARE_COVERAGE"],
    "encounters.csv": ["Id", "START", "STOP", "PATIENT", "ENCOUNTERCLASS", "DESCRIPTION", "TOTAL_CLAIM_COST"],
    "conditions.csv": ["START", "PATIENT", "ENCOUNTER", "CODE", "DESCRIPTION"],
    "medications.csv": ["START", "PATIENT", "ENCOUNTER", "CODE", "DESCRIPTION"],
    "procedures.csv": ["START", "PATIENT", "ENCOUNTER", "CODE", "DESCRIPTION"],
    "observations.csv": ["DATE", "PATIENT", "ENCOUNTER", "CODE", "DESCRIPTION", "VALUE", "UNITS"],
}


def validate_file(file_name, required_columns):
    file_path = RAW_DIR / file_name

    result = {
        "file_name": file_name,
        "exists": file_path.exists(),
        "row_count": None,
        "column_count": None,
        "missing_required_columns": None,
        "duplicate_id_count": None,
        "status": "not checked"
    }

    if not file_path.exists():
        result["status"] = "missing file"
        return result

    try:
        df = pd.read_csv(file_path, low_memory=False)

        result["row_count"] = len(df)
        result["column_count"] = len(df.columns)

        missing_columns = [col for col in required_columns if col not in df.columns]
        result["missing_required_columns"] = ", ".join(missing_columns) if missing_columns else ""

        if "Id" in df.columns:
            result["duplicate_id_count"] = int(df["Id"].duplicated().sum())
        elif "ID" in df.columns:
            result["duplicate_id_count"] = int(df["ID"].duplicated().sum())
        else:
            result["duplicate_id_count"] = ""

        result["status"] = "pass" if not missing_columns else "missing columns"

    except Exception as error:
        result["status"] = f"error: {error}"

    return result


def main():
    results = []

    print("Validating Synthea CSV files...\n")

    for file_name, required_columns in CORE_FILES.items():
        result = validate_file(file_name, required_columns)
        results.append(result)

        print(f"{file_name}: {result['status']}")
        print(f"  Rows: {result['row_count']}")
        print(f"  Columns: {result['column_count']}")
        print(f"  Missing columns: {result['missing_required_columns']}")
        print(f"  Duplicate IDs: {result['duplicate_id_count']}")
        print()

    report = pd.DataFrame(results)
    output_path = OUTPUT_DIR / "data_quality_report.csv"
    report.to_csv(output_path, index=False)

    print(f"Data quality report created: {output_path}")


if __name__ == "__main__":
    main()