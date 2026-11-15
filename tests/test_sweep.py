import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from sweep import decode_to  # noqa: E402


def test_decode_to_stops_at_limit():
    # flags 0, literal run of 4, long back-ref (5 bytes), then the next block starts
    stream = bytes([0x00, 0x03, 1, 2, 3, 4, 0x43, 3])
    rom = stream + bytes([0x00]) + bytes(0x2000000)
    data, end, st = decode_to(rom, 0, len(stream))
    assert (data, end, st) == (bytes([1, 2, 3, 4, 1, 2, 3, 4, 1]), len(stream), "exact")


def test_decode_to_flags_bad_reference():
    rom = bytes([0x00, 0x43, 0x05]) + bytes(0x2000000)
    assert decode_to(rom, 0, 3)[2] == "err"
