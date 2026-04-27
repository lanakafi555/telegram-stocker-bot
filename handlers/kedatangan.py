from config import ALLOWED_USERS
from utils.formatter import format_qty
from utils.sheets import sheet_database, sheet_kedatangan
from utils.lot_generator import generate_lot


def get_lookup_barang():
    data = sheet_database.get_all_records()
    return {row["alias"]: row for row in data}


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
            barang, qty, prod_exp = line.split()

            barang_data = lookup_barang.get(barang)

            if not barang_data:
                await update.message.reply_text(f"❌ Barang '{barang}' tidak terdaftar")
                failed += 1
                continue

            nama_barang = barang_data["nama_barang"]
            supplier = barang_data["supplier"]
            alamat = barang_data["alamat"]
            negara = barang_data["negara"]

            qty = format_qty(qty)
            kode_lot = generate_lot(sheet_kedatangan)

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