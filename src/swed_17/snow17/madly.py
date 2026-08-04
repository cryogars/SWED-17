from swed_17.snow17.swe_db import SweDB, S17ZonalSWE
import pandas as pd

class MADLY(SweDB):
    """
    Query class for the MADLY table.
    """
    UofA = "UofA"
    SNODAS = "SNODAS"

    class Query:
        """
        Subclass with all query components
        """
        ZDAYS = [f"zday{i:02d}" for i in range(1, 32)]
        BASE = (
            f"SELECT {", ".join(ZDAYS)}, mon, cal_yr FROM madly "
            "WHERE id = :id AND drain = :drain AND pos = :pos AND cgroup = 'F'"
        )

        PRODUCT = " AND pe1 = 'S' AND pe2 = 'W' AND dur = 'D' AND t = 'M'"
        UofA = " AND s='N'"
        SNODAS = " AND s='D'"
        YEAR = " AND cal_yr >= :from_year"

    def flatten_days(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Flatten the dataframe to have one row per day

        Parameters
        ----------
        df : pd.DataFrame
            Dataframe with MADLY data

        Returns
        -------
        pd.DataFrame
            Dataframe with one row per day
        """
        df = df.melt(
            id_vars=["Year", "Month"],
            value_vars=self.Query.ZDAYS,
            var_name="Day",
            value_name=S17ZonalSWE.SWE_COLUMN,
        )
        # Parse and drop invalid entries
        df["Day"] = df["Day"].str.replace("zday", "").astype(int)
        df = df[~(df.values == -9999).any(axis=1)]

        df = S17ZonalSWE.create_time_index(df)

        return S17ZonalSWE.swe_to_mm(df[[S17ZonalSWE.SWE_COLUMN]])

    def to_df(self, zone_id: str, product: str, from_year: int) -> pd.DataFrame:
        """
        Get MADLY data for a given segment

        Parameters
        ----------
        zone_id : str
            Snow-17 model segment name (8 character long, Example: ALEC2HUF)
        product : str
            Product to query (UofA, SNODAS)
        from_year : int, optional
            Filter for records after this year (Default: None)

        Returns
        -------
        pd.DataFrame
            DataFrame with MADLY data
        """
        if product == self.UofA:
            query = self.Query.BASE + self.Query.PRODUCT + self.Query.UofA + self.Query.YEAR
        elif product == self.SNODAS:
            query = self.Query.BASE + self.Query.PRODUCT + self.Query.SNODAS + self.Query.YEAR

        id = zone_id[0:5]
        drain = zone_id[5:6]
        pos = zone_id[6:7]

        params = {"id": id, "drain": drain, "pos": pos, "from_year": from_year}
        df = self.query(query, dataframe=True, **params)

        df.rename(columns={"cal_yr": "Year", "mon": "Month"}, inplace=True)
        df = self.flatten_days(df).sort_index()

        return df
