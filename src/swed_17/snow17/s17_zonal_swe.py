import pandas as pd


class S17ZonalSWE:
    """
    Zonal SWE query result transformer

    This is a helper class to transform a db query result into a pandas
    dataframe
    """
    INCH_TO_MM = 25.4
    SWE_COLUMN = 'SWE (in)'
    SWE_COLUMN_MM = 'SWE (mm)'
    COLUMN_MAPPING = [
        "Segment",
        "Zone Name",
        "Year",
        "Month",
        "Day",
        SWE_COLUMN,
    ]

    @classmethod
    def as_df(cls, df: pd.DataFrame):
        df.columns = cls.COLUMN_MAPPING
        df = cls.create_time_index(df)
        df = cls.swe_to_mm(df)
        return df

    @classmethod
    def create_time_index(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Concatenate the date columns (year, month, day) and set as index on
        the dataframe.
        """
        df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
        df = df.drop(columns=['Year', 'Month', 'Day'])
        return df.set_index('Date')

    @classmethod
    def swe_to_mm(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert SWE column to mm and rename in the dataframe
        """
        df[cls.SWE_COLUMN] *= cls.INCH_TO_MM
        return df.rename(
            columns={cls.SWE_COLUMN: cls.SWE_COLUMN_MM}
        )
