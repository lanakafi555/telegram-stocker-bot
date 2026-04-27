from datetime import datetime
import pytz

from config import ALLOWED_USERS, kamus_keterangan
from utils.formatter import format_qty
from utils.sheets import sheet_dry, sheet_frozen, sheet_database


def get_lookup_barang():
    data = sheet_database.get_all_records()
    return {row["alias"]: row for row in data}


async def handle_belanja(update, context):
    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        return

    user = ALLOWED_USERS[user_id]

    lookup_barang = get_lookup_barang()

    text = update.message.text.lower()
    lines = text.split("\n")

    timezone = pytz.timezone("Asia/Jakarta")
    jam = datetime.now(timezone).strftime("%H.%M")

    success = 0
    failed = 0

    for line in lines:
        if not line.strip():
            continue

        try:
            barang, kode, qty, ket = line.split()

            barang_data = lookup_barang.get(barang)

            if not barang_data:
                await update.message.reply_text(f"❌ Barang '{barang}' tidak terdaftar")
                failed += 1
                continue

            nama_barang = barang_data["nama_barang"]
            tipe = barang_data["tipe"].lower()

            qty = format_qty(qty)
            keterangan = kamus_keterangan.get(ket, ket)

            if tipe == "frozen":
                target_sheet = sheet_frozen
            else:
                target_sheet = sheet_dry

            target_sheet.append_row([
                nama_barang,
                kode,
                jam,
                qty,
                user,
                keterangan
            ])

            success += 1

        except Exception as e:
            print(e)
            failed += 1

    await update.message.reply_text(
        f"🧾 Belanja\n✅ {success} berhasil\n❌ {failed} gagal"
    )