from Crypto.Cipher import AES
import base64
import requests
import json

def crypt_request(server_url, data, secret_key):
    if not isinstance(data, str):
        data = json.dumps(data)
    ciphertext = encrypt_val(data, secret_key)
    data = {'data': ciphertext}
    r = requests.post(server_url, data=data, timeout=10, proxies={"http": "", "https": ""})
    try:
        r = json.loads(r.text)
    except:
        r = r.text
    return r

def encrypt_val(clear_text, secret_key):
    enc_secret = AES.new(secret_key[:32])
    tag_string = (str(clear_text) +
                  (AES.block_size -
                   len(str(clear_text)) % AES.block_size) * "\0")
    cipher_text = base64.b64encode(enc_secret.encrypt(tag_string))
    return cipher_text

def decrypt_val(cipher_text, secret_key):
    dec_secret = AES.new(secret_key[:32])
    raw_decrypted = dec_secret.decrypt(base64.b64decode(cipher_text))
    clear_val = raw_decrypted.rstrip("\0")
    return clear_val
