def translate_set(value, target_type):
    if target_type == "set":
        return value
    elif target_type == "list":
        return set_to_list(value)
    else:
        raise ValueError(f"Unsupported target type for translation from set: {target_type}")

def set_to_list(input_set):
    return list(input_set)