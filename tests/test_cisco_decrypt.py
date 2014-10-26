#!/usr/bin/env python
# coding=utf-8

"""
test_cisco_decrypt
----------------------------------

Tests for `cisco_decrypt` module.
"""

from . import os, codecs, hashlib, unittest

import cisco_decrypt as m


class TestCiscoDecrypt(unittest.TestCase):
    def test_sha1_bytes(self):
        r = os.urandom(64)
        hashlib_hash = hashlib.sha1(r).digest()
        package_hash = m._sha1(r)

        self.assertEqual(hashlib_hash, package_hash)

    def test_sha1_hexstr(self):
        r = codecs.encode(os.urandom(64), 'hex')
        hashlib_hash = hashlib.sha1(r).digest()
        package_hash = m._sha1(r)

        self.assertEqual(hashlib_hash, package_hash)

    def test_decrypt(self):
        enc = "D06615FC4D2046942A6F39951FC40794740E30C485090B4416C9D5A65DE59E" \
              "5230A63D391F2A634820B574A37E16DB23820C89CD29DA2245"
        plaintext = 'Sh@r3dK3ySP*&%$'

        self.assertEqual(m.decrypt(enc), plaintext)

    def test_notvalid_type(self):
        with self.assertRaises(m.CiscoDecryptionError):
            m.decrypt([])

    def test_notvalid_length(self):
        with self.assertRaises(m.CiscoDecryptionError):
            m.decrypt(b'')

    def test_notvalid_checksum(self):
        with self.assertRaises(m.CiscoDecryptionError):
            m.decrypt(os.urandom(48))

if __name__ == '__main__':
    unittest.main()
