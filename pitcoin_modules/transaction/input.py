import json


class Input:
    def __init__(self, txid, vout, scriptsig):
        self.txid = txid
        self.vout = vout
        self.scriptsig = scriptsig

