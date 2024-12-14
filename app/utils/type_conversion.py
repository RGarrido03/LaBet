def str_to_bool(s: str) -> bool:
    match s:
        case "True" | "true" | 1:
            return True
        case "False" | "false" | 0:
            return False
        case _:
            raise ValueError("Invalid string value. Use 'True' or 'False'.")
