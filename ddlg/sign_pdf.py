#!/usr/bin/env vpython3
# *-* coding: utf-8 *-*


import sys

import os

from OpenSSL.crypto import load_pkcs12
from endesive import pdf
# from 'endesive/pdf/endesive.py' import pdf

import datetime

#import logging
#logging.basicConfig(level=logging.DEBUG)



def getSignedPath(pathIn):
  # basename0 = os.path.basename(pathIn)
  # dirname = ""

  pathOut = pathIn.replace('.pdf', '_SIGNED.pdf')

  print(pathIn)
  print(pathOut)

  return pathOut

def main():

    # print("xxxxx")
    # print(sys.argv[-1])
    # print(sys.argv)
    # dct = {
    #     b'sigflags': 3,
    #     b'contact': b'mak@trisoft.com.pl',
    #     b'location': b'Szczecin',
    #     b'signingdate': b'20180731082642+02\'00\'',
    #     b'reason': b'Dokument podpisany cyfrowo',
    # }
    print("sys.argv")
    print(sys.argv)

    signdate = datetime.datetime.now().strftime("%Y%m%d%H%M%S").encode()
    dct = {
        b'sigflags': 3,
        b'contact': b'director@ddlghq.com',
        b'location': b'Bangkok',
        b'signingdate': signdate,
        b'reason': b'Digital signing after manually signed.',
    }
    # p12 = load_pkcs12(open('tests/fixtures/demo2_user1.p12', 'rb').read(), b'1234')
    p12 = load_pkcs12(open('CubikaChatbot-2019-06-10-210225.p12', 'rb').read(), b'password')
    # fname = '2.pdf'
    # fname = 'TSD_303_EN.pdf'
    # fname = 'en.pdf'
    # fname = 'pdf_files/jasper.pdf'
    # fname = 'pdf_files/google.pdf'
    # fname = 'pdf_files/word_print.pdf'

    fname = 'pdf_files/Acrobat-th-ลายเซ็น-signed-cms.pdf'
    fileOut = ''
    if len(sys.argv) == 2:
        fname = sys.argv[-1]
        fileOut = getSignedPath(fname)
    if len(sys.argv) == 3:
        fname = sys.argv[-2]
        fileOut = sys.argv[-1]

    print("input file")
    print(fname)

    print("output file")
    print(fileOut)

    datau = open(fname, 'rb').read()
    datas = pdf.cms.sign(datau, dct,
        p12.get_privatekey().to_cryptography_key(),
        p12.get_certificate().to_cryptography(),
        [],
        'sha256'
    )


    # fileOut = getSignedPath(fname)

    # fileOut = fname.replace('.pdf', '_SIGNED.pdf')
    with open(fileOut, 'wb') as fp:
        fp.write(datau)
        fp.write(datas)


main()
