from pitcoin_modules.block import Block
from pitcoin_modules.transaction import Deserializer, Transaction
from pitcoin_modules.transaction.tx_validator import check_tx_validity
import pickle
from pathlib import Path
from pitcoin_modules import PROJECT_ROOT


class BlocksStorage:
    def __init__(self, filepath=PROJECT_ROOT+'/storage/.blocks.txt'):
        self.storage_filepath = filepath

    def get_all_blocks(self):
        blocks_list = []
        if not Path(self.storage_filepath).is_file():
            Path(self.storage_filepath).touch()
        else:
            with open(self.storage_filepath, 'rb') as fp:
                try:
                    blocks_list = pickle.load(fp)
                except EOFError:
                    blocks_list = []
        return blocks_list

    def get_all_transactions_from_blocks(self):
        transactions = []
        blocks_list = self.get_all_blocks()
        for block in blocks_list:
            for tx in block.transactions:
                transactions.append(Deserializer.deserialize_transaction(tx))
        return transactions

    def get_transaction_by_txid(self, txid):
        transaction = []
        blocks_list = self.get_all_blocks()
        for block in blocks_list:
            for tx in block.transactions:
                deserialized = Deserializer.deserialize_transaction(tx)
                if deserialized.txid == txid:
                    transaction.append(deserialized)
        return transaction

    def add_block_to_storage(self, b: Block):
        blocks_list = self.get_all_blocks()
        if not b.validate_all_transactions():
            return False
        if len(blocks_list) != 0:
            if blocks_list[-1].hash_value != b.previous_hash:
                return False
        blocks_list.append(b)
        with open(self.storage_filepath, 'wb+') as fp:
            pickle.dump(blocks_list, fp)
        return True

    def get_last_block(self):
        blocks_list = self.get_all_blocks()
        if len(blocks_list) == 0:
            return None
        return blocks_list[-1]

    def get_last_n_blocks(self, n):
        blocks_list = self.get_all_blocks()
        if len(blocks_list) == 0:
            return None
        if len(blocks_list) < n:
            return blocks_list
        return blocks_list[-n:]

    def delete_all_blocks_from_mempool(self):
        blocks_list = []
        with open(self.storage_filepath, 'wb+') as fp:
            pickle.dump(blocks_list, fp)
        return True

    def get_blocks_count(self):
        blocks_list = self.get_all_blocks()
        return len(blocks_list)
