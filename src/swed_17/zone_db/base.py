from contextlib import contextmanager
from typing import ClassVar

import pandas as pd
from psycopg import Cursor
from psycopg.rows import TupleRow
from psycopg_pool import ConnectionPool
from sqlalchemy import create_engine


class Base:
    """
    Base database query class.
    """

    CONNECTION_OPTIONS: ClassVar[dict] = {
        "autocommit": True,
    }

    PSYCOPG_PROTOCOL = "postgresql+psycopg://"

    class Query:
        """
        Set of pre-defined database queries.
        """
        ZONE_AS_RASTER = "SELECT ST_AsGDALRaster(ST_Union(zone_mask.rast), 'GTiff') " \
                         "FROM zone_mask_as_raster(%(zone_name)s) AS zone_mask"

    def __init__(self, connection_info: str):
        self._connection_info = connection_info
        self._pool = ConnectionPool(
            connection_info,
            kwargs=self.CONNECTION_OPTIONS,
            min_size=1,
            max_size=4,
            check=ConnectionPool.check_connection,
        )
        self.engine = create_engine(self.pd_connection_info())

    @contextmanager
    def query(
        self,
        query: str,
        params: dict | None = None,
        row_factory: dict | None = None,
    ) -> Cursor[TupleRow]:
        """
        Execute given query by passing in requested parameters.

        This uses a conextmanager to manage the DB connection and to yield
        the results as DB cursor.

        Parameters
        ----------
        query : str
            SQL query
        params : dict, optional
            Pass in query parameters if the query contains any, by default {}
        row_factory: dict, optional
            Specify the class to use to parse each result row

        Returns
        -------
        Cursor
            Cursor with result from psycopg execute().
        """
        if params is None:
            params = {}
        if row_factory is None:
            row_factory = {}

        with (
            self._pool.connection() as connection,
            connection.cursor() as cursor,
        ):
            if row_factory:
                cursor.row_factory = row_factory

            cursor.execute(query, params)
            yield cursor

    def write(
        self, dataframe: pd.DataFrame, table_name: str, mode: str = "append"
    ) -> None:
        """
        Write datafrme to the database

        Parameters
        ----------
        dataframe : pd.DataFrame
            Dataframe with the data. The column names have to match the table
            columns
        table_name : str
            Table name to write to
        mode : str, optional
            Mode for writing to the table, by default "append". Use "replace"
            to drop the table before writing.
        """

        with self.engine.connect() as connection:
            dataframe.to_sql(
                table_name,
                con=connection,
                if_exists=mode,
                index=False,
                method="multi",
                chunksize=1000,
            )

    def pd_connection_info(self):
        """
        Return the connection info for use with pandas.

        Pandas needs an explicit defintion in the string to indicate psycopg
        use.
        """
        if "://" in self._connection_info:
            connection_info = self._connection_info.split("://")[1]
        else:
            connection_info = "?" + self._connection_info

        return self.PSYCOPG_PROTOCOL + connection_info
