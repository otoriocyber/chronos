# Customized version of https://github.com/williballenthin/python-ntfs/blob/master/examples/parse_usnjrnl/parse_usnjrnl.py
"""
Parse a UsnJrnl:$J object into a CSV file.
inspired by parser-usnjrnl by Seth Nazarro (http://code.google.com/p/parser-usnjrnl/)
"""

import struct, datetime
from parsers.parser_base import ParserBase

class BadRecordException(Exception):
    def __init__(self):
        pass


flag_def = {
    0x00:       " ",
    0x01:       "Data in one or more named data streams for the file was overwritten.",
    0x02:       "The file or directory was added to.",
    0x04:       "The file or directory was truncated.",
    0x10:       "Data in one or more named data streams for the file was overwritten.",
    0x20:       "One or more named data streams for the file were added to.",
    0x40:       "One or more named data streams for the file was truncated.",
    0x100:      "The file or directory was created for the first time.",
    0x200:      "The file or directory was deleted.",
    0x400:      "The user made a change to the file's or directory's extended attributes.",
    0x800:      "A change was made in the access rights to the file or directory.",
    0x1000:     "The file or directory was renamed and the file name in this structure is the previous name.",
    0x2000:     "The file or directory was renamed and the file name in this structure is the new name.",
    0x4000:     "A user toggled the FILE_ATTRIBUTE_NOT_CONTENT_INDEXED attribute.",
    0x8000:     "A user has either changed one or more file or directory attributes or one or more time stamps.",
    0x10000:    "An NTFS hard link was added to or removed from the file or directory",
    0x20000:    "The compression state of the file or directory was changed from or to compressed.",
    0x40000:    "The file or directory was encrypted or decrypted.",
    0x80000:    "The object identifier of the file or directory was changed.",
    0x100000:   "The reparse point contained in the file or directory was changed, or a reparse point was added to or deleted from the file or directory.",
    0x200000:   "A named stream has been added to or removed from the file or a named stream has been renamed.",
    0x80000000: "The file or directory was closed."
}


attrs_def = {
    1:    'READONLY',
    2:    'HIDDEN',
    4:    'SYSTEM',
    8:    '???',
    16:   'DIRECTORY',
    32:   'ARCHIVE',
    64:   'DEVICE',
    128:  'NORMAL',
    256:  'TEMPORARY',
    512:  'SPARSE_FILE',
    1024: 'REPARSE_POINT',
    2048: 'COMPRESSED',
    4096: 'OFFLINE',
    8192: 'NOT_CONTENT_INDEXED',
    16383:'ENCRYPTED',
    65536:'VIRTUAL'
}


def parse_windows_timestamp(qword):
    # see http://integriography.wordpress.com/2010/01/16/using-phython-to-parse-and-present-windows-64-bit-timestamps/
    return datetime.datetime.utcfromtimestamp(float(qword) * 1e-7 - 11644473600)


def MREF(mft_reference):
    """
    Given a MREF/mft_reference, return the record number part.
    """
    return mft_reference & 0xFFFFFFFFFFFF


def MSEQNO(mft_reference):
    """
    Given a MREF/mft_reference, return the sequence number part.
    """
    return (mft_reference >> 48) & 0xFFFF


def process_record(buf):
    try:
        offset = 0
        while True:
            record_size = buf[offset:]
            if record_size:
                try:
                    record_size = struct.unpack_from("<i", record_size)[0]
                except Exception as e:
                    print(e)
                    record_size = 0
                if record_size < 0:
                    raise BadRecordException
                if record_size < 60:
                    offset += 4
                else:
                    break
            else:
                break

        size, major, minor, file_ref, parent_ref, usn, timestamp, flags, source, sid, attrs, name_length, unknown = struct.unpack_from("<IHHQQQQIIIIHH", buf[offset:offset + record_size])
        name = buf[offset + 0x3C:offset + 0x3C + name_length].decode("utf16")
        return offset, size, major, minor, file_ref, parent_ref, usn, timestamp, flags, source, sid, attrs, name_length, unknown, name
    except Exception as e:
        return None


def get_json_list(filename, offset):
    with open(filename, "rb") as f:
        f_offset = 0

        # get file size
        f.seek(0, 2)
        f_length = f.tell()
        f_offset = offset
        f.seek(f_offset)

        # find start of data
        while f.read(32) == "\x00" * 32:
            f_offset += 655360 - 32
            f.seek(f_offset)

        if f_offset > 655360:
            f_offset -= 655360

        f.seek(f_offset)

        # data starts within the next 655360
        buf = f.read(655360)
        for i in range(len(buf)):
            if buf[i] != "\x00":
                f_offset += i
                f.seek(f_offset)
                break
            i += 1

        # we are at the main records now
        json_rows = []
        while True:
            buf = f.read(min((f_length - f_offset), 800))
            f.seek(f_offset)

            result = process_record(buf)
            if not result:
                return json_rows
            gap, size, major, minor, file_ref, parent_ref, usn, timestamp, flags, source, sid, attrs, name_length, unknown, name = result

            row = {
                "time": parse_windows_timestamp(timestamp).isoformat(),
                "filename": name,
                "file_attributes": " ".join([v for (k, v) in attrs_def.items() if attrs & k]),
                "reason": " ".join([v for (k, v) in flag_def.items() if flags & k])
            }

            json_rows.append(row)

            f_offset += gap + size
            if f_offset == f_length:
                break
            f.seek(f_offset)

        return json_rows


class UsnParser(ParserBase):
    FIELD_NAMES = ['Time', 'Filename', 'File attributes', 'Reason']

    def __init__(self, config):
        super().__init__(config)

    def parse(self, path):
        json_list = get_json_list(path, 0)
        self._write_results_tuple(("usnjournal", json_list))
