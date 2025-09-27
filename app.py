import logging
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, text
from sqlalchemy.orm import sessionmaker

class ExcelToSQLite:
    def __init__(self, db_name: str, log_file: str = "excel_to_sqlite.log"):
        self.engine = create_engine(f"sqlite:///{db_name}", echo=True)
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.logger = logging.getLogger("ExcelToSQLite")
        self.logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

        self.logger.info("Database initialized: %s", db_name)

    def load_excel(self, file_path: str) -> pd.DataFrame:
        df = pd.read_excel(file_path)
        return df

    def create_table_from_dataframe(self, df: pd.DataFrame, table_name: str):
        columns = []
        for col_name, dtype in zip(df.columns, df.dtypes):
            if "int" in str(dtype):
                col_type = Integer
            elif "float" in str(dtype):
                col_type = Float
            else:
                col_type = String

            columns.append(Column(col_name, col_type))

        table = Table(table_name, self.metadata, *columns, extend_existing=True)
        self.metadata.create_all(self.engine)
        return table

    def insert_dataframe(self, df: pd.DataFrame, table_name: str):
        df.to_sql(table_name, self.engine, if_exists="append", index=False)

    def query_all(self, table_name: str):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM {table_name}"))
                return result.fetchall()
        except Exception as e: 
            self.logger.exception("Error querying table %s: %s", table_name, e)
            return []

if __name__ == "__main__":
    excel_loader = ExcelToSQLite("mydata.db")

    # Step 1: Load Excel
    # df = excel_loader.load_excel("historical_invest_temp.xlsx")

    # Step 2: Create Table
    # excel_loader.create_table_from_dataframe(df, "investments")

    # Step 3: Insert Data
    # excel_loader.insert_dataframe(df, "investments")

    # Step 4: Query
    rows = excel_loader.query_all("investments")
    for row in rows:
        print(row)