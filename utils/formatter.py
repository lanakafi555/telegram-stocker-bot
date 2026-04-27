import re

def format_qty(qty):
    match = re.match(r"(\d+)([a-zA-Z]+)", qty)
    if match:
        return f"{match.group(1)} {match.group(2).lower()}"
    return qty