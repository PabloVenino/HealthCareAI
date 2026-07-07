import os
import unicodedata
import pandas as pd
from server.database.duckdb import get_db_client

# ---------------------------------------------------------------------------
# Column definitions — derived from data-dictionary.md
# ---------------------------------------------------------------------------

# Core columns: actively used by the application and AI reports
CORE_COLUMNS = [
    # Notification
    "NU_NOTIFIC", "DT_NOTIFIC", "DT_SIN_PRI",
    # Patient
    "CS_SEXO", "NU_IDADE_N",
    # Location
    "SG_UF", "SG_UF_NOT", "ID_MUNICIP",
    # Symptoms
    "FEBRE", "TOSSE", "GARGANTA", "DISPNEIA", "DESC_RESP", "SATURACAO",
    # Comorbidities
    "CARDIOPATI", "DIABETES", "ASMA", "OBESIDADE", "PNEUMOPATI", "RENAL", "IMUNODEPRE",
    # Hospitalization
    "HOSPITAL", "DT_INTERNA", "UTI", "SUPORT_VEN",
    # Laboratory
    "CLASSI_FIN", "PCR_SARS2", "PCR_FLUASU", "PCR_FLUBLI",
    # Vaccination
    "VACINA_COV",
    # Outcome
    "EVOLUCAO",
]

# Secondary columns: stored but not actively used by the AI
SECONDARY_COLUMNS = [
    # Patient
    "DT_NASC", "TP_IDADE", "CS_RACA",
    # Location
    "ID_REGIONA",
    # Symptoms
    "DIARREIA", "VOMITO", "FADIGA", "PERD_OLFT", "PERD_PALA",
    # Comorbidities
    "NEUROLOGIC", "HEMATOLOGI", "HEPATICA",
    # Hospitalization
    "DT_ENTUTI", "DT_SAIDUTI",
    # Laboratory
    "PCR_VSR", "PCR_RINO", "PCR_METAP",
    # Vaccination
    "DOSE_1_COV", "DOSE_2_COV", "DOSE_REF", "FAB_COV_1",
    # Outcome
    "DT_EVOLUCA",
]

# All columns to load from the raw CSV (Core + Secondary; Ignored are excluded at source)
COLUMNS_TO_LOAD = CORE_COLUMNS + SECONDARY_COLUMNS

# Date columns — pd.to_datetime will be applied to every column in this list
DATE_COLS = [
    "DT_NOTIFIC",   # Core — mandatory anchor date
    "DT_SIN_PRI",   # Core — symptom onset
    "DT_INTERNA",   # Core — hospital admission
    "DT_NASC",      # Secondary — birth date
    "DT_ENTUTI",    # Secondary — ICU entry
    "DT_SAIDUTI",   # Secondary — ICU exit
    "DOSE_1_COV",   # Secondary — first COVID dose
    "DOSE_2_COV",   # Secondary — second COVID dose
    "DOSE_REF",     # Secondary — booster dose
    "DT_EVOLUCA",   # Secondary — outcome date
]

# Boolean columns — normalized to '1' (Yes) / '2' (No) / '9' (Unknown)
BOOLEAN_COLS = [
    # Symptoms (Core)
    "FEBRE", "TOSSE", "GARGANTA", "DISPNEIA", "DESC_RESP", "SATURACAO",
    # Comorbidities (Core)
    "CARDIOPATI", "DIABETES", "ASMA", "OBESIDADE", "PNEUMOPATI", "RENAL", "IMUNODEPRE",
    # Hospitalization (Core)
    "HOSPITAL", "UTI", "SUPORT_VEN",
    # Vaccination (Core)
    "VACINA_COV",
    # Symptoms (Secondary)
    "DIARREIA", "VOMITO", "FADIGA", "PERD_OLFT", "PERD_PALA",
    # Comorbidities (Secondary)
    "NEUROLOGIC", "HEMATOLOGI", "HEPATICA",
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def normalize_text(series: pd.Series) -> pd.Series:
    """
    Normalize a free-text column entered by health workers:
      1. Fill NaN with empty string
      2. Strip surrounding whitespace
      3. Convert to UPPERCASE
      4. Remove diacritics/accents via Unicode NFKD decomposition
      5. Restore NaN for values that were originally empty/NaN

    Example: "São Paulo" → "SAO PAULO", "  rio de janeiro  " → "RIO DE JANEIRO"
    This eliminates duplicate city names caused by accent/casing variation in GROUP BY queries.
    """
    normalized = (
        series
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
        .apply(
            lambda s: unicodedata.normalize("NFKD", s)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    )
    return normalized.replace("", pd.NA)


def _normalize_boolean(series: pd.Series) -> pd.Series:
    """
    Normalize a coded boolean column to string '1', '2', or '9'.
    Raw values are often floats (e.g. 1.0) due to CSV int+NaN mixing — the
    .str.split('.').str[0] step handles this by stripping the decimal part.
    """
    cleaned = series.astype(str).str.split(".").str[0].str.strip()
    cleaned.loc[~cleaned.isin(["1", "2"])] = "9"
    return cleaned


# ---------------------------------------------------------------------------
# DataLoader
# ---------------------------------------------------------------------------

class DataLoader:
    def __init__(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.raw_path = os.path.join(self.root_dir, "data", "raw", "INFLUD19-23-03-2026.csv")
        self.processed_path = os.path.join(self.root_dir, "data", "processed", "cleaned.parquet")

    def ensure_data_ready(self) -> str:
        """
        Ensures the data is cleaned and saved to parquet, and returns the path to the
        parquet file. Also registers the parquet file as a DuckDB view for SQL queries.
        """
        os.makedirs(os.path.join(self.root_dir, "data", "processed"), exist_ok=True)

        if not os.path.exists(self.processed_path):
            if not os.path.exists(self.raw_path):
                raise FileNotFoundError(f"Raw data file not found at: {self.raw_path}")

            print(f"Cleaning raw data and saving to {self.processed_path}...")
            self.clean_data()

        # Register a DuckDB view for easier SQL queries
        db = get_db_client()
        db.execute_query(
            f"CREATE OR REPLACE VIEW srag AS SELECT * FROM read_parquet('{self.processed_path.replace(os.sep, '/')}');"
        )

        return self.processed_path

    def clean_data(self):
        """
        Loads the raw SRAG CSV, applies all cleaning rules defined in data-dictionary.md,
        and saves the result to a compact Parquet file.

        Cleaning pipeline:
          1. Load only Core + Secondary columns (Ignored columns excluded at source).
          2. Parse all date columns with error coercion.
          3. Drop rows with a missing DT_NOTIFIC (mandatory anchor).
          4. Normalize boolean columns to '1' / '2' / '9'.
          5. Fix EVOLUCAO to retain value '3' (Death by other cause).
          6. Normalize CLASSI_FIN to valid classification codes.
          7. Normalize free-text column ID_MUNICIP (strip, upper, remove accents).
          8. Normalize state code columns SG_UF and SG_UF_NOT.
          9. Cast NU_IDADE_N to nullable integer.
        """
        # Determine which of our desired columns actually exist in this CSV version;
        # the schema can vary slightly across dataset releases.
        available_cols = pd.read_csv(
            self.raw_path, nrows=0, sep=";", encoding="latin1"
        ).columns.tolist()
        cols_to_read = [c for c in COLUMNS_TO_LOAD if c in available_cols]
        missing = set(COLUMNS_TO_LOAD) - set(cols_to_read)
        if missing:
            print(f"[DataLoader] Warning: expected columns not found in CSV: {missing}")

        df = pd.read_csv(
            self.raw_path,
            usecols=cols_to_read,
            sep=";",
            encoding="latin1",
            low_memory=False,
        )
        print(f"[DataLoader] Loaded {len(df):,} rows x {len(df.columns)} columns.")

        date_cols_present = [c for c in DATE_COLS if c in df.columns]
        for col in date_cols_present:
            df[col] = pd.to_datetime(df[col], errors="coerce", format="mixed", dayfirst=True)

        before = len(df)
        df = df.dropna(subset=["DT_NOTIFIC"])
        dropped = before - len(df)
        if dropped:
            print(f"[DataLoader] Dropped {dropped:,} rows with missing DT_NOTIFIC.")

        bool_cols_present = [c for c in BOOLEAN_COLS if c in df.columns]
        for col in bool_cols_present:
            df[col] = _normalize_boolean(df[col])

        # Valid values per data dictionary: 1 (Cure), 2 (Death by SRAG), 3 (Death by other cause)
        # Previously '3' was incorrectly overwritten to '9', corrupting mortality metrics.
        if "EVOLUCAO" in df.columns:
            df["EVOLUCAO"] = df["EVOLUCAO"].astype(str).str.split(".").str[0].str.strip()
            df.loc[~df["EVOLUCAO"].isin(["1", "2", "3"]), "EVOLUCAO"] = "9"

        # Valid values: 1 (Influenza), 2 (Other Virus), 3 (Other Agent), 4 (Unspecified), 5 (COVID-19)
        if "CLASSI_FIN" in df.columns:
            df["CLASSI_FIN"] = df["CLASSI_FIN"].astype(str).str.split(".").str[0].str.strip()
            df.loc[~df["CLASSI_FIN"].isin(["1", "2", "3", "4", "5"]), "CLASSI_FIN"] = "9"

        # Municipality names are typed by health workers and can have accent/casing variation.
        # normalize_text() strips whitespace, uppercases, and removes diacritics.
        if "ID_MUNICIP" in df.columns:
            df["ID_MUNICIP"] = normalize_text(df["ID_MUNICIP"])

        # These are standardized 2-letter codes (e.g. 'SP', 'RJ') but we sanitize defensively.
        # SG_UF = State of Residence (Core); SG_UF_NOT = State of Notification (Secondary).
        for col in ["SG_UF", "SG_UF_NOT"]:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .fillna("UNKNOWN")
                    .astype(str)
                    .str.strip()
                    .str.upper()
                )

        # Protects against string-based aggregation errors in DuckDB if the CSV has messy entries.
        if "NU_IDADE_N" in df.columns:
            df["NU_IDADE_N"] = pd.to_numeric(df["NU_IDADE_N"], errors="coerce").astype("Int64")

        df.to_parquet(self.processed_path, index=False)
        print(f"[DataLoader] Cleaning complete. Saved {len(df):,} rows to {self.processed_path}.")


if __name__ == "__main__":
    loader = DataLoader()
    loader.ensure_data_ready()
