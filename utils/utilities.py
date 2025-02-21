from io import StringIO
from typing import Optional

import pandas as pd
from fastapi import UploadFile
from pandas.core.interchange.dataframe_protocol import DataFrame

from utils.exceptions import InvalidFileException


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


async def validate_csv_return_dataframe(file: UploadFile,type:str):
        """ Validates and parses CSV data """
        invalid_rows=[]
        if not file.filename.endswith(".csv"):
            raise InvalidFileException("Only CSV files are allowed")

        # Read CSV content
        contents = await file.read()
        try:
            csv_io = StringIO(contents.decode("utf-8"))
            df = pd.read_csv(csv_io)
        except Exception:
            raise InvalidFileException("Invalid CSV format")

        # Remove rows with any null or empty values

        #remove columns if all the values are numm
        df.dropna( how="all",axis=1, inplace=True)
        #rows
        df.dropna (how="all",inplace=True)

        df.replace("", float("nan"), inplace=True)

        if type=="member":
            required_headers =  ["name", "surname", "booking_count", "date_joined"]
        else:
            required_headers = ["title","description","remaining_count","expiration_date"]

        if not all(header in df.columns for header in required_headers):
            print("Not all required headers are present in the DataFrame")
            raise KeyError("All required headers are not present")

        df = df[required_headers]

        if type=="member":
            duplicates = df[df.duplicated(keep="first",subset=['name', 'surname'])]
            df.drop_duplicates(inplace=True, keep="first",subset=['name', 'surname'])
        else:
            duplicates = df[df.duplicated(keep="first", subset=['title'])]
            df.drop_duplicates(inplace=True, keep="first", subset=['title'])

        if not duplicates.empty:
            for _, row in duplicates.iterrows():
                invalid_rows.append(row.to_dict())

        for _, row in df.iterrows():
            if row.isnull().any():  # Check if any column has NaN
                invalid_rows.append(row.to_dict())

        df.dropna(inplace=True)  # Drop empty string rows again

        return df,invalid_rows