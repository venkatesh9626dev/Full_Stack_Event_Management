from uuid import UUID


def str_to_binary(uuid_str: str):
    return UUID(uuid_str).bytes


def binary_to_str(binary: bytes):
    return str(UUID(bytes=binary))
