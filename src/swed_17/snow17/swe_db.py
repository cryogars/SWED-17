from sqlalchemy import create_engine, text
import pandas as pd

from .s17_zonal_swe import S17ZonalSWE


class SweDB:
    """
    Class to interact with the Snow-17 DB
    """

    # SUFFIX in the segment names indiciate the type of record
    CALIBRATED = "_C"
    FORECASTED = "_F"

    class Query:
        ZONE_QUERY = (
            "SELECT segid, opid, cal_yr, mon, zday, swe "
            "FROM states_snow17 "
            "WHERE segid = :segid"
        )

    def __init__(self, connection_info: str) -> None:
        self._connection_info = connection_info

    def query(
        self, query: str, dataframe=True, **kwargs
    ) -> list | pd.DataFrame:
        """
        Execute a query for initialized connection string

        Parameters
        ----------
        query : str
            SQL query with optional parameters given via the kwargs
        dataframe: bool
            Return results as pandas dataframe (Default: True)

        Returns
        -------
        list or DataFrame
            Query result
        """
        engine = create_engine(self._connection_info)
        with engine.connect() as connection:
            if dataframe:
                result = pd.read_sql_query(
                    text(query), engine, params=kwargs
                )
            else:
                cursor = connection.execute(text(query), kwargs)
                result = cursor.fetchall()

        return result

    def for_zone_calibrated(
        self, segid: str, opid: str = None, from_year: int = None
    ) -> pd.DataFrame:
        """
        Get calibrated SWE zone data

        Parameters
        ----------
        segid : str
            Snow-17 model segment name
        opid : str
            CBRFC zone name (Optional)
        from_year : int
            First year to start returning data for up to present

        Returns
        -------
        pd.DataFrame
            Zone data for all available years.
        """
        # The '_C' suffix indicates calibrated segment records
        segid = segid + self.CALIBRATED

        return self.for_zone(segid, opid, from_year)

    def for_zone_forecasted(
        self, segid: str, opid: str = None, from_year: int = None
    ) -> pd.DataFrame:
        """
        Get forecasted SWE zone data

        Parameters
        ----------
        segid : str
            Snow-17 model segment name
        opid : str
            CBRFC zone name (Optional)
        from_year : int
            First year to start returning data for up to present

        Returns
        -------
        pd.DataFrame
            Zone data for all available years.
        """
        # The '_F' suffix indicates forecasted segment records
        segid = segid + self.FORECASTED

        return self.for_zone(segid, opid, from_year)

    def for_zone(
        self, segid: str, opid: str = None, from_year: int = None
    ) -> pd.DataFrame:
        """
        Get SWE zone data

        Parameters
        ----------
        segid : str
            Snow-17 model segment name
        opid : str
            CBRFC zone name (Optional)
        from_year : int
            First year to start returning data for up to present

        Returns
        -------
        pd.DataFrame
            Zone data for all available years.
        """

        query = self.Query.ZONE_QUERY
        query_args = {'segid': segid}

        if opid is not None:
            query = query + " AND opid = :opid"
            query_args['opid'] = opid

        if from_year is not None:
            query = query + " AND cal_yr >= :cal_yr"
            query_args["cal_yr"] = from_year

        data = S17ZonalSWE.as_df(
            self.query(query, **query_args)
        )

        return data
