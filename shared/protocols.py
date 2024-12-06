def encode_command(command_type, param1, param2):
    """
    Erstellt eine Nachricht im Protokollformat.
    """
    return f"{command_type},{param1},{param2}\n"


def decode_message(message):
    """
    Dekodiert eine Nachricht und gibt sie als Tupel zurück.
    """
    parts = message.strip().split(',')
    if len(parts) != 3:
        raise ValueError("Ungültiges Nachrichtenformat")
    return parts[0], int(parts[1]), int(parts[2])
