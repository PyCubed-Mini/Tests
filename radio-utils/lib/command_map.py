commands = {
    "NO_OP": [b'\x00\x00', False],
    "HARD_RESET": [b'\x00\x01', False],
    "QUERY": [b'\x00\x03', True],
    "EXEC_PY": [b'\x00\x04', False],
    "REQUEST_FILE": [b'\x00\x05', True],
    "LIST_DIR": [b'\x00\x06', True],
    "TQ_LEN": [b'\x00\x07', True],
}
