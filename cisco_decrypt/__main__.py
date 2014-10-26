# coding=utf-8

import os
import re
import sys
import codecs

import argparse

from six import print_

from . import decrypt, CiscoDecryptionError, DecodeError


PCF_ENCFIELD_RE = re.compile(r'^enc_([^=]+)\s*=([^$]+)$')


class StoreArg(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        files = set()
        hashes = set()
        for key, value in values:
            if key == 'file':
                files.add(value)
            elif key == 'hash':
                hashes.add(value)
            else:
                raise ValueError('unkown key %r returned for value %r'
                                 % (key, value))

        setattr(namespace, 'files', list(files))
        setattr(namespace, 'hashes', list(hashes))


def _file_or_hash(arg):
    if os.path.exists(arg):
        return ('file', os.path.realpath(arg))

    try:
        data = codecs.decode(arg, 'hex')
        if len(data) < 48:
            raise argparse.ArgumentTypeError(
                '%r is not a long enough hash to be an encrypted password'
                % arg
            )
        return ('hash', data)
    except DecodeError:
        pass

    raise argparse.ArgumentTypeError('%r is not a file or a hash' % arg)


def run_args(args):
    if args.hashes:
        for data in args.hashes:
            try:
                print_(decrypt(data))
            except CiscoDecryptionError as e:
                print_(
                    'Failed to decrypt %r, %s' % (data, e.message),
                    file=sys.stderr
                )

    if args.files:
        for path in args.files:
            basename = os.path.splitext(os.path.basename(path))[0]

            with open(path, 'r') as fp:
                lines = fp.read().splitlines()

            fields = filter(None, map(PCF_ENCFIELD_RE.match, lines))
            for field, hexhash in (match.groups() for match in fields):
                try:
                    plaintext = decrypt(hexhash)
                except CiscoDecryptionError as e:
                    print_("%s:%s:Error %s" % (basename, field, e.message))
                else:
                    print_("%s:%s:%s" % (basename, field, plaintext))
    pass


def main(argv=()):
    parser = argparse.ArgumentParser(
        description='Decrypt encryped passwords in Cisco pcf files',
        epilog="""Arguments can either be a pcf file with at least one
        enc_FIELD field within to decrypt or an encrypted hash to decrypt. If
        any hashes are present (determined if the operating system say it's not
        a path to a file and can be successfully decoded from a hex string to a
        byte array), they will be outputted in order presented first, followed
        by any files in the form: filename:FIELD:plaintext"""
    )

    parser.add_argument(
        'args',
        action=StoreArg,
        nargs='+',
        type=_file_or_hash,
        help='File to parse or hash to decode',
        metavar='file_or_hash'
    )

    args = parser.parse_args(argv or sys.argv)

    run_args(args)

if __name__ == '__main__':
    main()
