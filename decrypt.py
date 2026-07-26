import sys
from base64 import b64decode
from Crypto.Cipher import AES


def decrypt_file(enc_path, key_b64):
    with open(enc_path, "rb") as f:
        data = f.read()
    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]
    key = b64decode(key_b64)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    out_path = enc_path.replace(".enc", "")
    with open(out_path, "wb") as f:
        f.write(plaintext)
    print(f"Decrypte -> {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python decrypt.py <fichier.enc> <cle_base64>")
        sys.exit(1)
    decrypt_file(sys.argv[1], sys.argv[2])
