def list_to_table(rows: list[tuple], columns: list[str]):
    rows = [(str(x) for x in row) for row in rows]
    res = [
        " | ".join(["{:<15}".format(col) for col in row]) for row in rows
    ]

    return " | ".join(["{:<15}".format(col) for col in columns]) + "\n" + "\n".join(res)



