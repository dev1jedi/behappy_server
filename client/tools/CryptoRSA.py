import rsa
import json

class Crypto:
    def generate_keys(self):
        our_public_key, our_private_key = rsa.newkeys(2048)
        return our_public_key.save_pkcs1("PEM").decode("utf-8"), our_private_key.save_pkcs1("PEM").decode("utf-8")

    def load_pem_key(self, key: str):
        return rsa.PublicKey.load_pkcs1(key.encode("utf-8"))

    def load_pem_priv_key(self, key: str):
        return rsa.PrivateKey.load_pkcs1(key.encode("utf-8"))

    def encrypt(self, message: str, our_public_key) -> str:
        our_public_key = self.load_pem_key(our_public_key)
        result = []
        for n in range(0, len(message), 245):
            part = message[n:n + 245]
            result.append(rsa.encrypt(part.encode("utf-8"), our_public_key).decode("latin-1"))

        return ''.join(result)

    def decrypt(self, message: str, our_private_key):
        our_private_key = self.load_pem_priv_key(our_private_key)
        result = []
        for n in range(0, len(message), 256):
            part = message[n:n + 256]
            result.append(rsa.decrypt(bytes(part.replace("\uFFFD", "\x00"), encoding='latin-1'), our_private_key).decode())
        return ''.join(result)

