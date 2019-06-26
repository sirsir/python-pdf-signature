#!/usr/bin/env vpython3
# coding: utf-8
import unittest
import os
import sys
import io
from subprocess import PIPE, Popen
from datetime import datetime

from OpenSSL import crypto
from endesive import email

import hashlib
from asn1crypto import cms, algos, core, pem, x509

tests_root = os.path.dirname(__file__)
fixtures_dir = os.path.join(tests_root, 'fixtures')


def fixture(fname):
    return os.path.join(fixtures_dir, fname)


class EMAILTests(unittest.TestCase):
    def test_email_signed_attr(self):
        with open(fixture('demo2_user1.p12'), 'rb') as fh:
            p12 = crypto.load_pkcs12(fh.read(), b'1234')
        with open(fixture('smime-unsigned.txt'), 'rb') as fh:
            datau = fh.read()
        datas = email.sign(datau,
            p12.get_privatekey().to_cryptography_key(),
            p12.get_certificate().to_cryptography(),
            [],
            'sha256',
            attrs=True
        )
        fname = fixture('smime-signed-attr.txt')
        with open(fname, 'wb') as fh:
            fh.write(datas)

        cmd = [
            'openssl', 'smime', '-verify',
            '-CAfile', fixture('demo2_ca.crt.pem'),
            '-in', fname, '-inform', 'SMIME',
        ]
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        assert stderr == b'Verification successful\n'
        assert datau.replace(b'\n', b'\r\n') == stdout

    def test_email_signed_attr_custom(self):
        with open(fixture('demo2_user1.p12'), 'rb') as fh:
            p12 = crypto.load_pkcs12(fh.read(), b'1234')
        with open(fixture('smime-unsigned.txt'), 'rb') as fh:
            datau = fh.read()

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
        fname = fixture('smime-signed-attr-custom.txt')
        with open(fname, 'wb') as fh:
            fh.write(datas)

        cmd = [
            'openssl', 'smime', '-verify',
            '-CAfile', fixture('demo2_ca.crt.pem'),
            '-in', fname, '-inform', 'SMIME',
        ]
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        assert stderr == b'Verification successful\n'
        assert datau.replace(b'\n', b'\r\n') == stdout

    def test_email_signed_noattr(self):
        with open(fixture('demo2_user1.p12'), 'rb') as fh:
            p12 = crypto.load_pkcs12(fh.read(), b'1234')
        with open(fixture('smime-unsigned.txt'), 'rb') as fh:
            datau = fh.read()
        datas = email.sign(datau,
            p12.get_privatekey().to_cryptography_key(),
            p12.get_certificate().to_cryptography(),
            [],
            'sha256',
            attrs=False
        )
        fname = fixture('smime-signed-noattr.txt')
        with open(fname, 'wb') as fh:
            fh.write(datas)

        cmd = [
            'openssl', 'smime', '-verify',
            '-CAfile', fixture('demo2_ca.crt.pem'),
            '-in', fname, '-inform', 'SMIME',
        ]
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        assert stderr == b'Verification successful\n'
        assert datau.replace(b'\n', b'\r\n') == stdout

    def test_email_crypt(self):
        def load_cert(fname):
            with open(fname, 'rb') as f:
                cert_bytes = f.read()
                return crypto.load_certificate(crypto.FILETYPE_PEM, cert_bytes)
        certs = (
            load_cert(fixture('demo2_user1.crt.pem')),
        )
        with open(fixture('smime-unsigned.txt'), 'rb') as fh:
            datau = fh.read()
        datae = email.encrypt(datau, certs, 'aes256_ofb')
        fname = fixture('smime-encrypted.txt')
        with open(fname, 'wt') as fh:
            fh.write(datae)

        with open(fixture('demo2_user1.key.pem'), 'rb') as fh:
            key = crypto.load_privatekey(crypto.FILETYPE_PEM, fh.read(), b'1234')
        key = key.to_cryptography_key()
        with io.open(fname, 'rt', encoding='utf-8') as fh:
            datae = fh.read()
        datad = email.decrypt(datae, key)

        assert datau == datad

    def test_email_ssl_decrypt(self):
        def load_cert(fname):
            with open(fname, 'rb') as f:
                cert_bytes = f.read()
                return crypto.load_certificate(crypto.FILETYPE_PEM, cert_bytes)
        certs = (
            load_cert(fixture('demo2_user1.crt.pem')),
        )
        with open(fixture('smime-unsigned.txt'), 'rb') as fh:
            datau = fh.read()
        datae = email.encrypt(datau, certs, 'aes256_ofb')
        fname = fixture('smime-encrypted.txt')
        with open(fname, 'wt') as fh:
            fh.write(datae)

        cmd = [
            'openssl', 'smime', '-decrypt',
            '-recip', fixture('demo2_user1.crt.pem'), '-inkey', fixture('demo2_user1.key.pem'),
            '-in', fname,
        ]
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        assert stderr == b''
        lastbyte = stdout[-1]
        stdout = stdout[:len(stdout)-lastbyte]
        assert stdout == datau

    def test_email_ssl_encrypt(self):
        cmd = [
            'openssl', 'smime', '-encrypt', '-aes256',
            '-in', fixture('smime-unsigned.txt'),
            '-out', fixture('smime-ssl-encrypted.txt'),
            fixture('demo2_user1.crt.pem'),
        ]
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        assert stderr == b''
        assert stdout == b''

        with open(fixture('demo2_user1.key.pem'), 'rb') as fh:
            key = crypto.load_privatekey(crypto.FILETYPE_PEM, fh.read(), b'1234')
        key = key.to_cryptography_key()
        with io.open(fixture('smime-ssl-encrypted.txt'), 'rt', encoding='utf-8') as fh:
            datae = fh.read()
        datad = email.decrypt(datae, key)
        with open(fixture('smime-unsigned.txt'), 'rb') as fh:
            datau = fh.read()

        assert datau == datad.replace(b'\r\n', b'\n')
