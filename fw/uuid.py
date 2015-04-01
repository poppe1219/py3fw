"""Docstring"""

import os


def get_unique_id(length=1, upper=False):
    """Generates a modified UUID4 unique string.

    The return value will be (length * 32) of random hex characters.
    Length should be a number between 1 to 10, and defaults to 1.
    All characters in the result will be between 0 - 9 and between a - f.
    The code has been lifted from the Python uuid module and slimmed down.
    Dashes used in original uuid4's are not used, to save a little bit of
    data, since they don't contribute to the uniqueness of the id.
    The uuid's version number (4) is not used, again because it does not
    contribute to the uniqueness of the id.

    """
    uid = []
    index = 0
    while index < length:
        tmp = int(('%02x' * 16) % tuple(os.urandom(16)), 16)
        tmp &= ~(0xc000 << 48)
        tmp |= 0x8000 << 48
        tmp &= ~(0xf000 << 64)
        uid.append('%032x' % tmp)
        index += 1
    uid = ''.join(uid)
    if upper:
        uid = uid.upper()
    return uid
