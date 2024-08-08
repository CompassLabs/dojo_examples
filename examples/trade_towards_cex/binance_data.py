import csv
import io
import zipfile
from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests
from dateutil import parser as dateparser
from pytz import UTC


# SNIPPET 1 START
@dataclass
class Binance_data_point:
    """Represents a single line in the binance data."""

    open_time: datetime
    open_: float
    high: float
    low: float
    close: float
    volume: float
    close_time: datetime
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float
    ignore: int


class Binance_data:
    """Represents an entire binance data file."""

    def __init__(self, data: List[Binance_data_point]):
        self.data = data

    def find_nearest(self, target_time: datetime) -> Binance_data_point:
        """Slow method of find the data closest time to target_time.

        Removes all data prior or equal to target_time.
        """
        target_time.replace(tzinfo=UTC)
        while True:
            datum = self.data[0]
            if datum.close_time < target_time:
                self.data = self.data[1:]
            else:
                return datum
        return datum


def load_binance_data(year: int, month: int) -> Binance_data:
    url = f"https://data.binance.vision/data/spot/monthly/klines/ETHUSDC/1m/ETHUSDC-1m-{year}-{month:02}.zip"
    file_name = f"ETHUSDC-1m-{year}-{month:02}.csv"
    zipfile_data_raw = requests.get(url)
    zipfile_data = zipfile.ZipFile(io.BytesIO(zipfile_data_raw.content))
    csv_data_raw = zipfile_data.read(file_name).decode("UTF-8")
    csv_data = list(csv.reader(io.StringIO(csv_data_raw)))

    def binance_data_point_of_list(args: List[str]) -> Binance_data_point:
        return Binance_data_point(
            UTC.localize(datetime.fromtimestamp(float(args[0]) / 1000.0)),
            float(args[1]),
            float(args[2]),
            float(args[3]),
            float(args[4]),
            float(args[5]),
            UTC.localize(datetime.fromtimestamp(float(args[6]) / 1000.0)),
            float(args[7]),
            int(args[8]),
            float(args[9]),
            float(args[10]),
            int(args[11]),
        )

    return Binance_data([binance_data_point_of_list(datum) for datum in csv_data])


# SNIPPET 1 END
