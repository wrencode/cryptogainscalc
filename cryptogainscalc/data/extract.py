import os
from importlib import import_module
from itertools import chain
from pathlib import Path
from typing import Set

from dotenv import load_dotenv

from cryptogainscalc.data.dao.table import BaseTable

load_dotenv(Path(__file__).parent.parent.parent / ".env")

DATA_SOURCE = os.environ.get("DATA_SOURCE")


# noinspection PyPep8Naming
class TxData(object):
    def __init__(self, fiat_currency: str):
        data_source_module = f"cryptogainscalc.data.dao.{DATA_SOURCE.lower()}"
        data_source_class = f"{DATA_SOURCE.capitalize()}Table"
        DataTable = getattr(import_module(data_source_module), data_source_class)
        self.data: BaseTable = DataTable(
            fiat_currency,
            os.environ.get("GOOGLE_SHEETS_DOCUMENT_ID"),
            os.environ.get("GOOGLE_SHEETS_SHEET_NAME"),
            os.environ.get("GOOGLE_SHEETS_SHEET_COL_START"),
            os.environ.get("GOOGLE_SHEETS_SHEET_COL_END"),
        )

    def get_cryptocurrencies(self) -> Set[str]:
        return self.data.cryptocurrencies

    def retrieve_buy_events(
        self, tax_year: int, fiat_currency: str, sort_field: str, sort_direction: str
    ):
        return self.data.get_buy_events(
            tax_year=tax_year,
            fiat_currency=fiat_currency,
            sort_field=sort_field,
            sort_direction=sort_direction,
        )

    def retrieve_sell_events(
        self, tax_year: int, fiat_currency: str, sort_field: str, sort_direction: str
    ):
        return self.data.get_sell_events(
            tax_year=tax_year,
            fiat_currency=fiat_currency,
            sort_field=sort_field,
            sort_direction=sort_direction,
        )

    def retrieve_transact_events(
        self, tax_year: int, sort_field: str, sort_direction: str
    ):
        return self.data.get_transacts(
            tax_year=tax_year, sort_field=sort_field, sort_direction=sort_direction
        )

    def retrieve_nontaxable_events(
        self, tax_year: int, fiat_currency: str, sort_field: str, sort_direction: str
    ):
        return self.data.get_buy_events(
            tax_year=tax_year,
            fiat_currency=fiat_currency,
            sort_field=sort_field,
            sort_direction=sort_direction,
        )

    def retrieve_taxable_events(
        self, tax_year: int, fiat_currency: str, sort_field: str, sort_direction: str
    ):
        return list(
            chain(
                self.data.get_sell_events(
                    tax_year=tax_year,
                    fiat_currency=fiat_currency,
                    sort_field=sort_field,
                    sort_direction=sort_direction,
                ),
                self.data.get_transacts(
                    tax_year=tax_year,
                    sort_field=sort_field,
                    sort_direction=sort_direction,
                ),
            )
        )
