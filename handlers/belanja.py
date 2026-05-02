import re
from datetime import datetime
import pytz

from utils.sheets import sheet_dry, sheet_frozen, sheet_database


# ================= NORMALIZE =================
def normalize(text):
    return str(text).strip().lower()


# ================= FORMAT QTY =================
def format_qty(qty):
    match = re.match(r"(\d+)([a-zA-Z]+)", qty)
    if match:
        angka = match.group(1)
        satuan = match.group(2).lower()
        return f"{angka} {satuan}"
    return qty


# ================= AMBIL DATA BARANG =================
def get_barang_info(nama_input):
    data = sheet_database.get_all_records()
    nama_input = normalize(nama_input)

    for row in data:
        nama = normalize(row.get("nama_barang", ""))
        alias = normalize(row.get("alias", ""))

        if nama_input == nama or nama_input == alias:
            return row

    return None


# ================= HANDLE BELANJA =================
async def handle_belanja(update, context):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    lines = text.split("\n")

    timezone = pytz.timezone("Asia/Jakarta")
    jam = datetime.now(timezone).strftime("%H.%M")

    success_list = []
    error_list = []

    for line in lines:
        try:
            parts = line.strip().split()

            # validasi minimal input
            if len(parts) < 3:
                error_list.append(f"❌ Format salah: {line}")
                continue

            barang_input = parts[0]
            qty = parts[1]
            kode = parts[2]

            # ambil dari database
            info = get_barang_info(barang_input)

            if not info:
                error_list.append(f"❌ Tidak ditemukan: {barang_input}")
                continue

            nama_barang = info["nama_barang"]
            kategori = info.get("tipe", "dry")  # default dry
            keterangan = info.get("keterangan", "-")

            qty_formatted = format_qty(qty)

            # pilih sheet otomatis
            if normalize(kategori) == "frozen":
                target_sheet = sheet_frozen
                kategori_label = "Frozen"
            else:
                target_sheet = sheet_dry
                kategori_label = "Dry"

            # simpan ke sheet
            target_sheet.append_row([
                nama_barang,
                kode,
                jam,
                qty_formatted,
                user_id,
                keterangan
            ])

            # simpan untuk summary
            success_list.append(f"- {nama_barang.title()} ({qty_formatted})")

        except Exception as e:
            print("ERROR BELANJA:", e)
            error_list.append(f"❌ Error: {line}")

    # ================= OUTPUT =================
    messages = []

    if success_list:
        success_text = "✅ Berhasil input:\n" + "\n".join(success_list)
        messages.append(success_text)

    if error_list:
        error_text = "\n".join(error_list)
        messages.append(error_text)

    if messages:
        await update.message.reply_text("\n\n".join(messages))