import os
import json
import gspread

from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS"])

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict,
    scope
)
client = gspread.authorize(creds)


# ================= FILE DATABASE =================
spreadsheet_db = client.open_by_key(
    "1JUfMdbaxisCQD-e-ggJhROThq544_eKELW2uVJt_1q4"
)

sheet_database = spreadsheet_db.worksheet(
    "database_barang"
)


# ================= FILE BELANJA =================
spreadsheet_belanja = client.open_by_key(
    "1JCt60WaLLuELWzuVX1lo_K_FlGoEyLaML8LiBePkb-E"
)

sheet_kedatangan = spreadsheet_db.worksheet("kedatangan_barang")
sheet_invoice = spreadsheet_db.worksheet("invoice_log")

def get_next_invoice_number(today):
    records = sheet_invoice.get_all_records()

    today_records = [
        r for r in records if str(r.get("tanggal", "")) == today
    ]

    if not today_records:
        return 1

    last_number = max(int(r["nomor"]) for r in today_records)
    return last_number + 1
