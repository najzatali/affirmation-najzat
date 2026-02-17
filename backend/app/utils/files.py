import io


def read_upload_file(upload_file) -> bytes:
    return upload_file.file.read()


def bytes_io(data: bytes) -> io.BytesIO:
    return io.BytesIO(data)
