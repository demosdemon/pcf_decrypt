========
Usage
========

To use Cisco PCF Decrypt in a project::

    import pcf_decrypt

The command line script::

    usage: pcf_decrypt [-h] file_or_hash [file_or_hash ...]

    Decrypt encryped passwords in Cisco pcf files

    positional arguments:
      file_or_hash  File to parse or hash to decode

    optional arguments:
      -h, --help    show this help message and exit

    Arguments can either be a pcf file with at least one enc_FIELD field within to
    decrypt or an encrypted hash to decrypt. If any hashes are present (determined
    if the operating system say it's not a path to a file and can be successfully
    decoded from a hex string to a byte array), they will be outputted in order
    presented first, followed by any files in the form: filename:FIELD:plaintext
