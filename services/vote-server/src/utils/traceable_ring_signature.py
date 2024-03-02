import hashlib


class TraceableRingSignature:
    def __init__(self, ring_size, public_key, private_key):
        self.ring_size = ring_size
        self.public_key = public_key
        self.private_key = private_key

    def sign(self, message, public_keys):
        message_hash = hashlib.sha256(message.encode()).hexdigest()

    def verify(self, message, signature):
        pass
