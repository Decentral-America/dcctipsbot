from base64 import b64encode, b64decode
from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Random import get_random_bytes
from nacl import pwhash
from nacl.exceptions import InvalidkeyError
from typing import Dict
from dtb.settings import KEY

opslimit = pwhash.argon2id.OPSLIMIT_MODERATE 
memlimit = pwhash.argon2id.MEMLIMIT_MODERATE  

def encrypt(plaintext) -> Dict:
    password = KEY.encode('utf8')
    #Argon 2id
    salt = get_random_bytes(pwhash.argon2id.SALTBYTES)
    derived_key = pwhash.argon2id.kdf(32, password, salt, opslimit=opslimit, memlimit=memlimit)
    pass_hash = pwhash.argon2id.str(password, opslimit=opslimit, memlimit=memlimit)
    #XChaCha20_Poly1305
    nonce = get_random_bytes(24)
    cipher = ChaCha20_Poly1305.new(key=derived_key, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    #Return JSON
    jk = [ 'salt', 'pass_hash', 'nonce', 'ciphertext', 'tag' ]
    jv = [ b64encode(x).decode('utf-8') for x in (salt, pass_hash, nonce, ciphertext, tag) ]
    result = dict(zip(jk, jv))
    return result

def decrypt(encrypted_dict) -> str:
    password = KEY.encode('utf8')
    try:
        jk = [ 'salt', 'pass_hash', 'nonce', 'ciphertext', 'tag' ]
        jv = {k:b64decode(encrypted_dict[k]) for k in jk}
        #Argon 2id
        pwhash.argon2id.verify(jv['pass_hash'], password)
        derived_key = pwhash.argon2id.kdf(32, password, jv['salt'], opslimit=opslimit, memlimit=memlimit)
        #ChaCha20_Poly1305
        cipher = ChaCha20_Poly1305.new(key=derived_key, nonce=jv['nonce'])
        plaintext = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag']).decode('utf-8')
        return plaintext
    except (ValueError, KeyError, InvalidkeyError):
        raise Exception("Incorrect decryption")