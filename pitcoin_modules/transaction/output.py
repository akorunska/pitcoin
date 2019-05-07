import json


class Output:
    def __init__(self, value, scriptpubkey, txid="", vout=0):
        self.value = value
        self.scriptpubkey = scriptpubkey
        self.txid = txid
        self.vout = vout

    def __eq__(self, other):
        return self.txid == other.txid and self.vout == other.vout

