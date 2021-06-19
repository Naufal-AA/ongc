from Crypto.Hash import SHA256
from base64 import b64decode
from base64 import b64encode

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

import os

class Encryptor:
    def __init__(self, key):
        hash_obj = SHA256.new(key.encode('utf-8'))
        self.key = hash_obj.digest()


    def encrypt(self, message, key):
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return b64encode(iv + cipher.encrypt(pad(message, AES.block_size)))

    def encrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            plaintext = fo.read()
        enc = self.encrypt(plaintext, self.key)
        with open(file_name + ".enc", 'wb') as fo:
            fo.write(enc)
        os.remove(file_name)

    def decrypt(self, ciphertext, key):
        iv = b64decode(ciphertext)
        cipher = AES.new(key, AES.MODE_CBC, iv[:AES.block_size])
        plaintext = unpad(cipher.decrypt(iv[AES.block_size:]), AES.block_size)
        return plaintext

    def decrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            ciphertext = fo.read()
        dec = self.decrypt(ciphertext, self.key)
        
        file = file_name
        filebase = file.split("media")
        filebase = filebase[0] + "media\\"
        filename = os.path.basename(file)
        filename = filename[:-4]
        filename =str(filebase) + str(filename)
        
        with open(filename, 'wb') as fo:
            fo.write(dec)


        
