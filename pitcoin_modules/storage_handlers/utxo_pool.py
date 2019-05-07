from pitcoin_modules.wallet import *
from pitcoin_modules.transaction import Transaction
from pitcoin_modules.transaction import Output
import pickle
from pathlib import Path
from pitcoin_modules import PROJECT_ROOT


class UTXOStorage:
    def __init__(self, filepath=PROJECT_ROOT+'/storage/.utxopool.txt'):
        self.storage_filepath = filepath

    def get_all_outputs(self):
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

    @staticmethod
    def __address_from_p2pkh_script(script: str):
        pubkey_hashed = script[6:len(script) - 4]
        return get_address_from_hashed_public_key(pubkey_hashed)

    @staticmethod
    def __hashed_pubkey_from_p2wpkh_script(script: str):
        pubkey_hashed = script[4:len(script)]
        return pubkey_hashed

    def get_all_unspent_outputs_for_address(self, address):
        res = []
        outp_list = self.get_all_outputs()
        if address[:2] == 'tb':
            for outp in outp_list:
                pubkey = self.__hashed_pubkey_from_p2wpkh_script(outp.scriptpubkey)
                if get_bech32_address_from_hashed_pubkey(pubkey) == address:
                    res.append(outp)
        else:
            for outp in outp_list:
                if self.__address_from_p2pkh_script(outp.scriptpubkey) == address:
                    res.append(outp)
        return res

    def contains_output(self, outp):
        outp_list = self.get_all_outputs()
        if outp in outp_list:
            return True
        return False

    def delete_ouput_if_exists(self, outp):
        if self.contains_output(outp):
            outp_list = self.get_all_outputs()
            for i in range(len(outp_list)):
                if outp_list[i] == outp:
                    del(outp_list[i])
                    break
            with open(self.storage_filepath, 'wb+') as fp:
                pickle.dump(outp_list, fp)
            return True
        return False

    def delete_all_otputs(self):
        outp_list = []
        with open(self.storage_filepath, 'wb+') as fp:
            pickle.dump(outp_list, fp)
        return True

    def add_new_output(self, outp):
        outp_list = self.get_all_outputs()
        outp_list.append(outp)
        with open(self.storage_filepath, 'wb+') as fp:
            pickle.dump(outp_list, fp)
        return True

    def update_with_new_transaction(self, tx: Transaction):
        outputs = self.get_all_outputs()
        for i in tx.inputs:
            used_output = Output(0, "", i.txid, i.vout)
            # todo ? return false if there is no such output
            self.delete_ouput_if_exists(used_output)
        for i, o in zip(range(1, len(tx.outputs) + 1), tx.outputs):
            o.txid = tx.txid
            o.vout = i
            self.add_new_output(o)
        return True


