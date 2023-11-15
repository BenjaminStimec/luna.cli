def translate_list(value, target_type):
    if target_type == "list":
        return value
    elif target_type == "set":
        return list_to_set(value)
    elif target_type == "tuple":
        return list_to_tuple(value)
    else:
        raise ValueError(f"Unsupported target type for translation from list: {target_type}")

def list_to_set(input_list):
    return set(input_list)

def list_to_tuple(input_list):
    return tuple(input_list)