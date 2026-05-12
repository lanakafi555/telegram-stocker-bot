from datetime import datetime
import pytz

from config import ALLOWED_USERS
from utils.sheets import sheet_invoice


# ================= BULAN INDONESIA =================
BULAN = {
    1: "JAN",
    2: "FEB",
    3: "MAR",
    4: "APR",
    5: "MEI",
    6: "JUN",
    7: "JUL",
    8: "AGS",
    9: "SEP",
    10: "OKT",
    11: "NOV",
    12: "DES"
}


# ================= GET NEXT NUMBER =================
def get_next_invoice_number(tanggal):

    data = sheet_invoice.get_all_records()

    highest = 0

    for row in data:

        row_tanggal = str(
            row.get("tanggal", "")
        ).strip()

        if row_tanggal != tanggal:
            continue

        try:

            nomor = int(
                row.get("nomor", 0)
            )

            if nomor > highest:
                highest = nomor

        except:
            pass

    return highest + 1


# ================= GENERATE =================
def generate_invoice(nama_supplier, nomor):

    timezone = pytz.timezone(
        "Asia/Jakarta"
    )

    now = datetime.now(timezone)

    # ================= FORMAT =================
    tanggal_sheet = now.strftime(
        "%d.%m.%y"
    )

    dd = now.strftime("%d")

    mm = now.strftime("%m")

    yy = now.strftime("%y")

    bulan = BULAN[now.month]

    # ================= KODE 1 =================
    kode1 = (
        f"SMPTRU.RI.{dd}.{mm}.{yy}.{nomor:02d}"
    )

    # ================= KODE 2 =================
    nama_clean = nama_supplier.upper()

    kode2 = (
        f"{dd}{bulan}{yy}_{nama_clean}_1271.SMPTRU"
    )

    return tanggal_sheet, kode1, kode2


# ================= HANDLER =================
async def handle_invoice(update, context):

    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        return

    nama_supplier = (
        update.message.text.strip()
    )

    timezone = pytz.timezone(
        "Asia/Jakarta"
    )

    now = datetime.now(timezone)

    tanggal_sheet = now.strftime(
        "%d.%m.%y"
    )

    # ================= NOMOR =================
    nomor = get_next_invoice_number(
        tanggal_sheet
    )

    # ================= GENERATE =================
    tanggal, kode1, kode2 = generate_invoice(
        nama_supplier,
        nomor
    )

    timestamp = now.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # ================= SAVE =================
    sheet_invoice.append_row([
        tanggal,
        nomor,
        nama_supplier,
        kode1,
        kode2,
        timestamp
    ])

    # ================= OUTPUT =================
    await update.message.reply_text(
        f"<code>{kode1}</code>\n"
        f"<code>{kode2}</code>",
        parse_mode="HTML"
    )
