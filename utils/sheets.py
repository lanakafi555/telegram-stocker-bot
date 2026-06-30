import os
import gspread

from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# ================= GOOGLE CREDS =================

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
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
    "17_K3qCBQ6ALNhJFM5NwudaTqm5j8qXtvCGZWJmg920o"
)

sheet_kedatangan = spreadsheet_db.worksheet("kedatangan_barang")
sheet_invoice = spreadsheet_db.worksheet("invoice_log")


def get_next_invoice_number(today):
    records = sheet_invoice.get_all_records()

    today_records = [
        r for r in records if str(r.get("tanggal", "")) == today
    ]

    return len(today_records) + 1
