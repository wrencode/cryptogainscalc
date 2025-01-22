# cryptogainscalc - Cryptocurrency Gains Calculator

Python utility to calculate cryptocurrency capital gains and losses from Google Sheets records.

## Setup

* Configure your Google credentials (see `auth/credentials.template.json`)
* Configure your `.env` file (see `.env.template`)
* Run `python auth/google_quickstart.py` to authenticate with Google

## Run

* Run `python main.py` (run `python main.py -h` to see command line options)
* View output in the command line *or* in `logs/out.log`
* View any exported CSV results in `output/` (if `-x/--export` flag was used)
