from dataclasses import dataclass

from psycopg.rows import class_row
from rasterio.io import MemoryFile

from swed_17 import ZoneDB


@dataclass
class CBRFCZoneRow:
    gid: int
    ch5_id: str
    zone: str
    description: str


class CBRFCZone(ZoneDB):
    ZONES_IN_CH5ID = "SELECT cz.gid, cz.ch5_id, cz.zone, cz.description " \
                     "FROM cbrfc_zones CZ " \
                     "WHERE CH5_ID = ANY(%s)"

    def zone_as_rio(self, zone_name: str) -> MemoryFile:
        """
        Query for a zone mask and return as a rasterio MemoryFile.

        Parameters
        ----------
        zone_name : str
            SQL query

        Returns
        -------
        MemoryFile
            Result of query as rasterio MemoryFile
        """
        with self.query(
            self.Query.ZONE_AS_RASTER, {'zone_name': zone_name}
        ) as db_result:
            result = db_result.fetchone()
        return MemoryFile(bytes(result[0]))

    def from_ch5_ids(self, ch5_ids: list) -> list[str]:
        """
        Return list of zone names for given CH5 IDs

        Parameters
        ----------
        ch5_ids : list
            CH5 IDs

        Returns
        -------
        Row
            List with zone names
        """
        with self.query(
            CBRFCZone.ZONES_IN_CH5ID,
            [ch5_ids],
            row_factory=class_row(CBRFCZoneRow)
        ) as db_result:
            return db_result.fetchall()

    def from_ch5_id(self, ch5_id: str) -> list[str]:
        """
        Return list of zone name for given CH5 ID

        Parameters
        ----------
        ch5_id : str
            CH5 ID

        Returns
        -------
        list[str]
            List with zone name
        """
        return self.zone_in_ch5_ids([ch5_id])
