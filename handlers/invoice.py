from utils.sheets import sheet_invoice, get_next_invoice_number
from utils.invoice_generator import generate_invoice
from datetime import datetime
import pytz

tz = pytz.timezone("Asia/Jakarta")

async def handle_invoice(update, context):
    text = update.message.text.strip()

    if not text:
        await update.message.reply_text("Format salah. Isi nama supplier.")
        return

    nama = " ".join(text.split())

    now = datetime.now(tz)
    today = now.strftime("%y.%m.%d")

    nomor = get_next_invoice_number(today)

    kode1, kode2, tanggal = generate_invoice(nama, nomor)

    sheet_invoice.append_row([
        tanggal,
        nomor,
        nama,
        kode1,
        kode2,
        now.strftime("%Y-%m-%d %H:%M:%S")
    ])

    await update.message.reply_text(
    f"<code>{kode1}</code>\n<code>{kode2}</code>",
    parse_mode="HTML"
)