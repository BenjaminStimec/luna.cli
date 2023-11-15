def accept_integer(value):
    if not isinstance(value, int):
        raise TypeError("Expected an integer")
    return f"Received integer: {value}"

def accept_boolean(value):
    if not isinstance(value, bool):
        raise TypeError("Expected a boolean")
    return f"Received boolean: {value}"

def accept_dictionary(value):
    if not isinstance(value, dict):
        raise TypeError("Expected a dictionary")
    return f"Received dictionary: {value}"

def accept_bytes(value):
    if not isinstance(value, bytes):
        raise TypeError("Expected bytes")
    return f"Received bytes: {value}"

def accept_complex(value):
    if not isinstance(value, complex):
        raise TypeError("Expected a complex number")
    return f"Received complex number: {value}"