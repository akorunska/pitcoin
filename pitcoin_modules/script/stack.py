import binascii
import codecs
import hashlib
from pitcoin_modules.wallet import check_message_signature

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, arg):
        self.stack.append(arg)

    def pop(self):
        if len(self.stack) == 0:
            return None
        arg = self.stack[-1]
        del(self.stack[-1])
        return arg

    def op_dup(self):
        self.stack.append(self.stack[-1])

    def op_hash160(self):
        arg = self.pop()
        sha_encrypted = hashlib.sha256(binascii.unhexlify(arg)).hexdigest()

        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(binascii.unhexlify(sha_encrypted))
        enc_160 = ripemd160.hexdigest()
        self.push(enc_160)

    def op_equal_verify(self):
        el1 = self.pop()
        el2 = self.pop()
        return el1 == el2

    def op_checksig(self, txid):
        pubkey = self.pop()
        pubkey = pubkey[2:len(pubkey)]
        sig = self.pop()
        self.push(check_message_signature(codecs.encode(pubkey), codecs.encode(sig), codecs.encode(txid)))

    def running_succeeded(self):
        if self.pop() == True:
            return True
        return False

    def __str__(self):
        return str(self.__dict__)
