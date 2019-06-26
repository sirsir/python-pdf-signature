#!/usr/bin/env vpython3
# *-* coding: utf-8 *-*
from OpenSSL.crypto import load_pkcs12
from endesive import email

import hashlib
from asn1crypto import cms, algos, core, pem, x509

def main():
    p12 = load_pkcs12(open('demo2_user1.p12', 'rb').read(), '1234')
    datau = open('smime-unsigned.txt', 'rb').read()

    datau1 = datau.replace(b'\n', b'\r\n')
    hashalgo = 'sha256'
    signed_value = getattr(hashlib, hashalgo)(datau1).digest()
    attrs = [
        cms.CMSAttribute({
            'type': cms.CMSAttributeType('1.2.840.113549.1.9.16.2.47'),
            'values': (algos.DigestAlgorithm({'algorithm': hashalgo}),),
        }),
        cms.CMSAttribute({
            'type': cms.CMSAttributeType('message_digest'),
            'values': (signed_value,),
        }),
    ]

    datas = email.sign(datau,
        p12.get_privatekey().to_cryptography_key(),
        p12.get_certificate().to_cryptography(),
        [],
        'sha256',
        attrs=attrs
    )
    open('smime-signed-attr-custom.txt', 'wb').write(datas)


main()
