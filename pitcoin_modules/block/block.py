import json

from pitcoin_modules.block.merkle import get_merkle_root
from pitcoin_modules.wallet.wallet import sha256_bytes_to_bytes
from pitcoin_modules.transaction import *
import codecs


class Block:
    def __init__(self, timestamp, previous_hash, transactions, nonce=0):
        self.timestamp = timestamp
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.transactions = transactions
        tx_list = [Deserializer.deserialize_transaction(tx) for tx in self.transactions]
        txid_list = [tx.txid for tx in tx_list]
        self.merkle_root = codecs.decode(get_merkle_root(txid_list), 'ascii')

        wtxid_list = [tx.wtxid for tx in tx_list[:-1]]
        if len(wtxid_list) > 0:
            self.sw_merkle_root = codecs.decode(get_merkle_root(wtxid_list), 'ascii')
        else:
            self.sw_merkle_root = ""
        self.hash_value = self.get_hash()

    def validate_all_transactions(self, tx_list=[]):
        # tx_are_valid = True
        # for tx in self.transactions:
        #     tx_are_valid = tx_are_valid and check_tx_validity(Deserializer.deserialize_transaction(tx), tx_list)
        # return tx_are_valid
        return True

    def get_hash(self):
        data = codecs.encode(self.timestamp, 'ascii') + codecs.encode(str(self.nonce), 'ascii') +\
            codecs.encode(self.previous_hash, 'ascii')
        for tx in self.transactions:
            data += codecs.encode(tx)
        data += codecs.encode(self.merkle_root, 'ascii')
        return codecs.decode(sha256_bytes_to_bytes(data), 'ascii')

    @staticmethod
    def from_json(json_str):
        block = Block(
            json_str['timestamp'],
            json_str['previous_hash'],
            [tx for tx in json_str['transactions']],
            json_str['nonce']
        )
        return block

    def __str__(self):
        return json.dumps(self.__dict__)
