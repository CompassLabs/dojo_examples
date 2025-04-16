"""Convert .db file to .json.

Dojo spits out files in sqlite(.db) format. This script converts them to .json format.
"""
from dojo.external_data_providers.exports.json_converter import convert_db_file_to_json

convert_db_file_to_json("example_backtest.db")
