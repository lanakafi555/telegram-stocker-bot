from gspread.utils import rowcol_to_a1


def append_custom(sheet, start_col, start_row, data):

    values = sheet.col_values(start_col)

    next_row = len(values) + 1

    if next_row < start_row:
        next_row = start_row

    start_cell = rowcol_to_a1(next_row, start_col)

    end_col = start_col + len(data) - 1
    end_cell = rowcol_to_a1(next_row, end_col)

    range_text = f"{start_cell}:{end_cell}"

    sheet.update(range_text, [data])

    return next_row