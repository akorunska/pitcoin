from pitcoin_modules.transaction import Deserializer, Transaction
from pitcoin_modules.transaction.tx_validator import check_tx_validity
import pickle
from pathlib import Path
from pitcoin_modules import PROJECT_ROOT


class MemPoolStorage:
    def __init__(self, filepath=PROJECT_ROOT+'/storage/.mempool.txt'):
        self.storage_filepath = filepath

    def get_validated_deserialized_transaction(self, data, transactions: list):
        tx = Deserializer.deserialize_transaction(data)
        if check_tx_validity(tx, transactions):
            return tx
        else:
            return None

    def add_serialized_transaction_to_mempool(self, data, transactions: list):
        tx = self.get_validated_deserialized_transaction(data, transactions)
        if tx is None:
            return False
        self.add_transaction_to_mempool(tx)
        return True

    def get_all_transactions(self):
        tx_list = []
        if not Path(self.storage_filepath).is_file():
            Path(self.storage_filepath).touch()
        else:
            with open(self.storage_filepath, 'rb') as fp:
                try:
                    tx_list = tx_list = pickle.load(fp)
                except EOFError:
                    tx_list = []
        return tx_list

    def add_transaction_to_mempool(self, tx):
        tx_list = self.get_all_transactions()
        tx_list.append(tx)
        with open(self.storage_filepath, 'wb+') as fp:
            pickle.dump(tx_list, fp)
        return True

    def contains_transaction(self, tx_to_find):
        tx_list = self.get_all_transactions()
        for tx in tx_list:
            if tx.txid == tx_to_find.txid:
                return True
        return False

    def delete_last_transaction_from_mempool(self):
        tx_list = self.get_all_transactions()
        tx_list.pop()
        with open(self.storage_filepath, 'wb+') as fp:
            pickle.dump(tx_list, fp)
        return True

    def delete_all_transactions_from_mempool(self):
        tx_list = []
        with open(self.storage_filepath, 'wb+') as fp:
            pickle.dump(tx_list, fp)
        return True

    def delete_transaction_if_exists(self, tx):
        if self.contains_transaction(tx):
            tx_list = self.get_all_transactions()
            for i in range(len(tx_list)):
                if tx_list[i] == tx:
                    del(tx_list[i])
                    break
            with open(self.storage_filepath, 'wb+') as fp:
                pickle.dump(tx_list, fp)
            return True
        return False

    def get_three_first_transactions(self):
        tx_list = self.get_all_transactions()

        if len(tx_list) >= 4:
            return tx_list[0:3]
        else:
            return tx_list

    def get_transactions_count(self):
        tx_list = self.get_all_transactions()
        return len(tx_list)

