import re
import pytz

from datetime import datetime

from config import ALLOWED_USERS

from utils.sheets import (
    sheet_database,
    spreadsheet_belanja
)

from utils.append import append_custom


# ================= NORMALIZE =================
def normalize(text):
    return str(text).strip().lower()


# ================= LOAD DATABASE =================
def load_database():

    data = sheet_database.get_all_records()

    database = {}

    for row in data:

        nama_barang = normalize(
            row.get("nama_barang", "")
        )

        alias = normalize(
            row.get("alias", "")
        )

        # ================= AMBIL TIPE =================
        kategori = normalize(
            row.get("tipe", "")
        )

        # ================= AMBIL KETERANGAN =================
        keterangan = row.get(
            "keterangan",
            "-"
        )

        item_data = {
            "nama": row.get("nama_barang"),
            "kategori": kategori,
            "keterangan": keterangan
        }

        # ================= NAMA BARANG =================
        if nama_barang:

            database[nama_barang] = item_data

        # ================= ALIAS =================
        if alias:

            database[alias] = item_data

    return database


# ================= PARSE INPUT =================
def parse_line(text):

    """
    Format:
    milo 2pack 060526.01

    hasil:
    nama = milo
    qty = 2 pack
    kode = 060526.01
    """

    pattern = r"(.+?)\s+(.+?)\s+([\d\.]+)$"

    match = re.match(
        pattern,
        text.strip(),
        re.IGNORECASE
    )

    if not match:
        return None

    nama = match.group(1).strip()

    qty_raw = match.group(2).strip()

    kode = match.group(3).strip()

    # ================= FORMAT QTY =================
    qty_match = re.match(
        r"(\d+)([a-zA-Z]+)",
        qty_raw
    )

    if qty_match:

        angka = qty_match.group(1)

        satuan = qty_match.group(2)

        qty = f"{angka} {satuan}"

    else:

        qty = qty_raw

    return {
        "nama": nama,
        "qty": qty,
        "kode": kode
    }


# ================= HANDLE BELANJA =================
async def handle_belanja(update, context):

    user_id = update.effective_user.id

    # ================= CEK AKSES =================
    if user_id not in ALLOWED_USERS:

        await update.message.reply_text(
            "❌ Kamu tidak memiliki akses."
        )

        return

    user = ALLOWED_USERS[user_id]

    text = update.message.text.strip()

    # ================= MULTILINE =================
    lines = text.split("\n")

    database = load_database()

    timezone = pytz.timezone("Asia/Jakarta")

    now = datetime.now(timezone)

    jam = now.strftime("%H.%M")

    # ================= SHEET HARIAN =================
    today_sheet = now.strftime("%d")

    sheet_harian = spreadsheet_belanja.worksheet(
        today_sheet
    )

    berhasil = []

    gagal = []

    # ================= LOOP INPUT =================
    for line in lines:

        parsed = parse_line(line)

        # ================= FORMAT SALAH =================
        if not parsed:

            gagal.append(
                f"❌ Format salah: {line}"
            )

            continue

        nama_input = normalize(
            parsed["nama"]
        )

        # ================= BARANG TIDAK ADA =================
        if nama_input not in database:

            gagal.append(
                f"❌ Tidak ditemukan: {parsed['nama']}"
            )

            continue

        barang = database[nama_input]

        nama_barang = barang["nama"]

        kategori = barang["kategori"]

        keterangan = barang["keterangan"]

        # ================= DATA ROW =================
        data_row = [
            nama_barang,
            parsed["kode"],
            jam,
            parsed["qty"],
            user,
            keterangan
        ]

        # ================= FROZEN =================
        if kategori == "frozen":

            append_custom(
                sheet_harian,
                13,  # M
                8,
                data_row
            )

        # ================= DRY =================
        else:

            append_custom(
                sheet_harian,
                3,  # C
                8,
                data_row
            )

        berhasil.append(
            f"✅ {nama_barang} ({parsed['qty']})"
        )

    # ================= OUTPUT =================
    hasil_text = ""

    # ================= BERHASIL =================
    if berhasil:

        hasil_text += "✅ Berhasil input:\n"

        for item in berhasil:

            hasil_text += f"- {item}\n"

    # ================= GAGAL =================
    if gagal:

        hasil_text += "\n❌ Gagal:\n"

        for item in gagal:

            hasil_text += f"- {item}\n"

    # ================= KIRIM HASIL =================
    await update.message.reply_text(
        hasil_text
    )
