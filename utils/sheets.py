import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)

spreadsheet = client.open("Stock Log")

sheet_dry = spreadsheet.worksheet("belanja_dry")
sheet_frozen = spreadsheet.worksheet("belanja_frozen")
sheet_database = spreadsheet.worksheet("database_barang")
sheet_kedatangan = spreadsheet.worksheet("kedatangan_barang")
sheet_invoice = spreadsheet.worksheet("invoice_log")

def get_next_invoice_number(today):
    records = sheet_invoice.get_all_records()

    today_records = [
        r for r in records if str(r.get("tanggal", "")) == today
    ]

    if not today_records:
        return 1

    last_number = max(int(r["nomor"]) for r in today_records)
    return last_number + 1