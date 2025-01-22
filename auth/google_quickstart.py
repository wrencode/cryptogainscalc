import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pandas import DataFrame
from pyloggingsetup import get_logger

root_dir = Path(__file__).parent.parent

logger = get_logger(__file__, log_dir=root_dir / "logs")

load_dotenv(root_dir / ".env")

# If modifying these scopes, delete the file token.json
# scopes can be found here: https://developers.google.com/identity/protocols/oauth2/scopes
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]

# The ID and range of a sample spreadsheet.
# noinspection SpellCheckingInspection
SAMPLE_SPREADSHEET_ID = f"{os.environ.get('GOOGLE_SHEETS_DOCUMENT_ID')}"
SAMPLE_RANGE_NAME = f"transactions!{os.environ.get('GOOGLE_SHEETS_SHEET_COL_START')}:{os.environ.get('GOOGLE_SHEETS_SHEET_COL_END')}"


def main():
    """Shows basic usage of the Sheets API & prints values from a sample spreadsheet."""

    google_auth_dir = root_dir / "auth"
    credentials_file_path = google_auth_dir / "credentials.json"
    if not google_auth_dir.exists():
        os.makedirs(google_auth_dir)
    token_file_path = google_auth_dir / "token.json"

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if token_file_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_file_path), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_file_path), SCOPES
            )
            with open(credentials_file_path, "r+") as cred_file:
                cred_json = json.load(cred_file)
                cred_file.seek(0)
                cred_file.truncate()
                json.dump(cred_json, cred_file, indent=2)

            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file_path, "w") as token:
            json.dump(json.loads(creds.to_json()), token, indent=2)

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            logger.warning("No data found.")
        else:
            cleaned_data = []
            for row in values:
                if row and row[0] != "":
                    cleaned_data.append([str.replace(cell, "\n", " ") for cell in row])
            df = DataFrame(cleaned_data[1:], columns=cleaned_data[0])
            df.index += 1
            # logger.info(f"\n{set(df['Tx Type'].tolist())}")
            logger.info(f"\n{df.to_string()}")

    except HttpError as err:
        logger.error(err)


if __name__ == "__main__":
    main()
