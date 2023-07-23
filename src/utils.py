import re
from pathlib import Path
from typing import Union


def read_file(filepath: Union[str, Path]) -> str:
    filepath = Path(filepath).resolve()

    if not filepath.exists():
        raise ValueError("File does not exist.")

    with open(filepath, "r") as file:
        content = file.read()

    return content


# https://stackoverflow.com/questions/2545532/python-analog-of-phps-natsort-function-sort-a-list-using-a-natural-order-alg
def natural_key(string_):
    """See https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]