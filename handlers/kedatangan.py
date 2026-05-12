import re
import pytz

from datetime import datetime

from config import ALLOWED_USERS

from utils.formatter import format_qty

from utils.sheets import (
    sheet_database,
    sheet_kedatangan
)


# ================= NORMALIZE =================
def normalize(text):
    return str(text).strip().lower()


# ================= LOAD DATABASE =================
def get_lookup_barang():

    data = sheet_database.get_all_records()

    lookup = {}

    for row in data:

        nama_barang = normalize(
            row.get("nama_barang", "")
        )

        alias = normalize(
            row.get("alias", "")
        )

        item_data = {
            "nama_barang": row.get("nama_barang"),
            "supplier": row.get("supplier"),
            "alamat": row.get("alamat"),
            "negara": row.get("negara")
        }

        if nama_barang:
            lookup[nama_barang] = item_data

        if alias:
            lookup[alias] = item_data

    return lookup


# ================= FORMAT QTY =================
def flexible_qty(qty_raw):

    match = re.match(
        r"(\d+)([a-zA-Z]+)",
        qty_raw
    )

    if match:

        angka = match.group(1)

        satuan = match.group(2)

        return f"{angka} {satuan}"

    return qty_raw


# ================= GENERATE LOT =================
def generate_lot(sheet, nama_barang):

    timezone = pytz.timezone(
        "Asia/Jakarta"
    )

    now = datetime.now(timezone)

    tanggal = now.strftime("%d%m%y")

    data = sheet.get_all_values()

    highest = 0

    for row in data:

        if len(row) < 2:
            continue

        row_barang = normalize(row[0])

        row_lot = str(row[1])

        # ================= CEK BARANG =================
        if row_barang != normalize(nama_barang):
            continue

        # ================= CEK TANGGAL =================
        if not row_lot.startswith(tanggal):
            continue

        try:

            nomor = int(
                row_lot.split(".")[1]
            )

            if nomor > highest:
                highest = nomor

        except:
            pass

    return f"{tanggal}.{highest + 1:02d}"


# ================= PARSE INPUT =================
def parse_line(text):

    """
    Format:
    milo 2karton 12Des2027
    """

    pattern = r"(.+?)\s+(.+?)\s+(.+)$"

    match = re.match(
        pattern,
        text.strip(),
        re.IGNORECASE
    )

    if not match:
        return None

    barang = match.group(1).strip()

    qty = flexible_qty(
        match.group(2).strip()
    )

    prod_exp = match.group(3).strip()

    return {
        "barang": barang,
        "qty": qty,
        "prod_exp": prod_exp
    }


# ================= HANDLE KEDATANGAN =================
async def handle_kedatangan(update, context):

    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        return

    user = ALLOWED_USERS[user_id]

    lookup_barang = get_lookup_barang()

    text = update.message.text.lower()

    lines = text.split("\n")

    success = 0

    failed = 0

    for line in lines:

        if not line.strip():
            continue

        try:

            parsed = parse_line(line)

            if not parsed:

                failed += 1

                continue

            barang_input = normalize(
                parsed["barang"]
            )

            barang_data = lookup_barang.get(
                barang_input
            )

            if not barang_data:

                await update.message.reply_text(
                    f"❌ Barang '{parsed['barang']}' tidak terdaftar"
                )

                failed += 1

                continue

            nama_barang = barang_data["nama_barang"]

            supplier = barang_data["supplier"]

            alamat = barang_data["alamat"]

            negara = barang_data["negara"]

            qty = parsed["qty"]

            prod_exp = parsed["prod_exp"]

            # ================= GENERATE LOT =================
            kode_lot = generate_lot(
                sheet_kedatangan,
                nama_barang
            )

            # ================= APPEND =================
            sheet_kedatangan.append_row([
                nama_barang,
                kode_lot,
                supplier,
                alamat,
                negara,
                qty,
                prod_exp,
                user
            ])

            success += 1

        except Exception as e:

            print(e)

            failed += 1

    await update.message.reply_text(
        f"📦 Kedatangan\n✅ {success} berhasil\n❌ {failed} gagal"
    )
