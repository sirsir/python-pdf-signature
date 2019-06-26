#!/usr/bin/env python3
# *-* coding: utf-8 *-*
from oscrypto import asymmetric
from endesive import pdf

def main():
    dct = {
        b'sigflags': 3,
        b'contact': b'me@email.com',
        b'location': b'City',
        b'signingdate': b'20180731082642+02\'00\'',
        b'reason': b'Some descriptive message',
    }
    p12 = asymmetric.load_pkcs12(
        open('CubikaChatbot-2019-06-10-210225.p12', 'rb').read(),
        'password'
    )
    datau = open('1.pdf', 'rb').read()
    datas = pdf.cms.sign(datau, dct, p12[0], p12[1], [], 'sha256')
    with open('pdf-signed-cms.pdf', 'wb') as fp:
        fp.write(datau)
        fp.write(datas)

main()