import argparse
import logging
import os
import sys
from logging import getLogger
from pathlib import Path

from dotenv import load_dotenv
from pyloggingsetup import get_logger

from cryptogainscalc.evaluate.capital import TaxableCrypto

root_dir = Path(__file__).parent

load_dotenv(root_dir / ".env")

getLogger("googleapiclient.discovery_cache").setLevel(level=logging.WARNING)

logger = get_logger(__file__, log_dir=root_dir / "logs")


def main(argv):
    arg_parser = argparse.ArgumentParser(
        description="Calculate cryptocurrency capital gains/losses from spreadsheet data."
    )

    # optional argument
    arg_parser.add_argument(
        "--tax_year",
        "-y",
        type=int,
        help="(Optional) Tax year for which to calculate capital gains/losses.",
    )

    # optional argument
    arg_parser.add_argument(
        "--fiat_currency",
        "-f",
        type=str,
        help='(Optional) Selected fiat currency. Default = "usd".',
    )

    # optional argument
    arg_parser.add_argument(
        "--sort_field",
        "-s",
        type=str,
        help='(Optional) Selected field on which to sort transactions. Default = "timestamp".',
    )

    # switch
    arg_parser.add_argument(
        "--lifo",
        "-l",
        action="store_true",
        help="(Optional) Boolean switch to turn on LIFO (descending). Default = FIFO (ascending).",
    )

    # optional argument
    arg_parser.add_argument(
        "--expenditure-types",
        "-e",
        nargs="+",
        default=[],
        help=(
            "(Optional) List of expenditure types from data source (spreadsheet). "
            'Default = ["purchase", "donation", "gift"].'
        ),
    )

    # switch
    arg_parser.add_argument(
        "--export",
        "-x",
        action="store_true",
        help="(Optional) Boolean switch to turn on export to CSV.",
    )

    args = arg_parser.parse_args(argv)

    taxable_crypto = TaxableCrypto(
        tax_year=args.tax_year,
        fiat_currency=args.fiat_currency if args.fiat_currency else "usd",
        sort_field=args.sort_field if args.sort_field else "timestamp",
        sort_direction="ascending" if args.lifo else "descending",
        expenditure_types=args.expenditure_types if args.expenditure_types else [],
    )

    capital_gains_and_losses_df = taxable_crypto.get_capital_gains_and_losses_df(
        exclude_columns=["cryptocurrency", "date_acquired", "date_sold"]
    )

    taxable_income_df = taxable_crypto.get_taxable_income_df(
        exclude_columns=["cryptocurrency", "date_acquired", "date_sold"]
    )

    if args.export:
        output_dir = Path(__file__).parent / "output"
        if not output_dir.exists():
            os.makedirs(output_dir)

        capital_gains_and_losses_df.to_csv(
            output_dir
            / (
                f"{f'{args.tax_year}-' if args.tax_year else ''}"
                f"cryptocurrency{f'_to_{args.fiat_currency}' if args.fiat_currency else ''}-"
                f"capital_gains_and_losses.csv"
            )
        )

        taxable_income_df.to_csv(
            output_dir
            / (
                f"{f'{args.tax_year}-' if args.tax_year else ''}"
                f"cryptocurrency{f'_to_{args.fiat_currency}' if args.fiat_currency else ''}-"
                f"taxable_income.csv"
            )
        )

    return capital_gains_and_losses_df, taxable_income_df


if __name__ == "__main__":
    capital_gains_and_losses_output, taxable_income_output = main(sys.argv[1:])
    logger.info(
        f"\n\nCAPITAL GAINS AND LOSSES\n{capital_gains_and_losses_output.to_string()}\n"
    )
    logger.info(f"\n\nTAXABLE INCOME\n{taxable_income_output.to_string()}\n")
