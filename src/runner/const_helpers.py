def csv2list(csv_str):
    """csv2list
    Converts a string of comma-separated values into a Python list of strs,
    stripping whitespace and disallowing empty strings from appearing in the
    final list.

    :param csv_str: String of comma-separated values
    """
    return list(filter(lambda s: s != '', map(str.strip, csv_str.split(','))))
