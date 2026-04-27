from datetime import datetime

def generate_lot(sheet):
    today = datetime.now().strftime("%d%m%y")

    data = sheet.get_all_values()

    count = 0
    for row in data[1:]:  # skip header
        if row[1].startswith(today):
            count += 1

    return f"{today}.{str(count+1).zfill(2)}"