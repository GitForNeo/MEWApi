# -*- coding: utf-8 -*-

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512, SHA384, SHA256, SHA, MD5
from Crypto import Random


def newkeys(keysize):
    random_generator = Random.new().read
    key = RSA.generate(keysize, random_generator)
    private, public = key, key.publickey()
    return public, private


def importkey(externkey):
    return RSA.importKey(externkey)


def getpublickey(priv_key):
    return priv_key.publickey()


def encrypt(message, pub_key):
    # RSA encryption protocol according to PKCS#1 OAEP
    cipher = PKCS1_OAEP.new(pub_key)
    return cipher.encrypt(message)


def decrypt(ciphertext, priv_key):
    # RSA encryption protocol according to PKCS#1 OAEP
    cipher = PKCS1_OAEP.new(priv_key)
    return cipher.decrypt(ciphertext)


def sign(message, priv_key, hash_alg="SHA-256"):
    signer = PKCS1_v1_5.new(priv_key)
    if hash_alg == "SHA-512":
        digest = SHA512.new()
    elif hash_alg == "SHA-384":
        digest = SHA384.new()
    elif hash_alg == "SHA-256":
        digest = SHA256.new()
    elif hash_alg == "SHA-1":
        digest = SHA.new()
    else:
        digest = MD5.new()
    digest.update(message)
    return signer.sign(digest)


def verify(message, signature, pub_key, hash_alg="SHA-256"):
    signer = PKCS1_v1_5.new(pub_key)
    if hash_alg == "SHA-512":
        digest = SHA512.new()
    elif hash_alg == "SHA-384":
        digest = SHA384.new()
    elif hash_alg == "SHA-256":
        digest = SHA256.new()
    elif hash_alg == "SHA-1":
        digest = SHA.new()
    else:
        digest = MD5.new()
    digest.update(message)
    return signer.verify(digest, signature)
