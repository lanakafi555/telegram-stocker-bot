from datetime import datetime
import pytz

tz = pytz.timezone("Asia/Jakarta")

def generate_invoice(nama, nomor):
    now = datetime.now(tz)

    tanggal1 = now.strftime("%y.%m.%d")        # 26.04.26
    tanggal2 = now.strftime("%d%b%y").upper()  # 26APR26

    kode1 = f"SMPTRU.RI.{tanggal1}.{nomor:02d}"
    kode2 = f"{tanggal2}_{nama.upper()}_1271.SMPTRU"

    return kode1, kode2, tanggal1