# coding=utf-8

__author__ = 'Joachim Brandon LeBlanc'
__email__ = 'demosdemon@gmail.com'
__version__ = '0.1.0'

import codecs

from Crypto.Cipher import DES3
from Crypto.Hash import SHA
from six import PY3, string_types, binary_type

__all__ = ['decrypt', 'CiscoDecryptionError', 'DecodeError']

if PY3:
    DecodeError = ValueError
else:
    DecodeError = TypeError


class CiscoDecryptionError(Exception):
    pass


def _sha1(data):
    if isinstance(data, string_types):
        try:
            data = codecs.encode(data, 'utf-8')
        except UnicodeDecodeError:
            if PY3:
                data = codecs.encode(codecs.decode(data, 'utf-8'), 'utf-8')
    if isinstance(data, bytearray):
        data = binary_type(data)

    return SHA.new(data).digest()


def decrypt(hex_or_bin):
    if not isinstance(hex_or_bin, (string_types, binary_type)):
        raise CiscoDecryptionError(
            "%r is not a valid data type." % type(hex_or_bin).__name__
        )

    try:
        data = codecs.decode(hex_or_bin, 'hex')
    except DecodeError:
        data = hex_or_bin
    pass

    if len(data) < 48:  # encrypted data is not long enough to be a cisco pswd
        raise CiscoDecryptionError(
            "Encrypted data is not long enough to be an encrypted Cisco "
            "password. Received length=%d" % (len(data) - 40, )
        )

    IV = data[:8]
    checksum = data[20:40]
    enc_data = data[40:]

    if _sha1(enc_data) != checksum:
        raise CiscoDecryptionError("Encrypted data failed checksum.")

    hset = bytearray(data[:20])
    hset[19] += 1

    key = _sha1(hset)

    hset[19] += 2

    key = key + _sha1(hset)[:4]

    k1, k2, k3 = tuple(key[i:i+8] for i in range(3))
    if k1 == k2 or k1 == k3 or k2 == k3:
        raise CiscoDecryptionError("Calculated key is not a valid DES3 key.")

    cipher = DES3.new(key, mode=DES3.MODE_CBC, IV=IV)

    plaintext = cipher.decrypt(enc_data)
    strip_len = plaintext[-1] if PY3 else ord(plaintext[-1])

    return codecs.decode(plaintext[:-strip_len], 'utf-8')
