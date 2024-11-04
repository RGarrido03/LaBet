import difflib
from typing import List, AnyStr


def get_most_similar_name(input_name, possible_names) -> List[AnyStr]:
    return difflib.get_close_matches(input_name, possible_names, n=1, cutoff=0.5)
