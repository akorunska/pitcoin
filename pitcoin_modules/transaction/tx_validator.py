from pitcoin_modules.wallet import sha256_str_to_str
from .transaction import Transaction, Serializer
from pitcoin_modules.script import run_script
from copy import deepcopy


def get_tx_by_txid(tx_list, txid):
    for tx in tx_list:
        if tx.txid == txid:
            return tx
    return None


def tx_list_to_txo_list(tx_list):
    txo_list = []
    for tx in tx_list:
        for i, output in zip(range(1, len(tx.outputs) + 1), tx.outputs):
            output.txid = tx.txid
            output.vout = i
            txo_list.append(output)
    return txo_list


def check_tx_validity(tx: Transaction, tx_list: list):
    if (tx.version == 2):
        return check_sw_tx_validity(tx, tx_list)
    for input in tx.inputs:
        tx_with_output_to_unlock = get_tx_by_txid(tx_list, input.txid)
        if not tx_with_output_to_unlock:
            return False
        if len(tx_with_output_to_unlock.outputs) < input.vout:
            return False
        output = tx_with_output_to_unlock.outputs[input.vout - 1]
        script = input.scriptsig + output.scriptpubkey

        input_copy = deepcopy(tx.inputs)
        msg = Serializer.construct_tx_data_as_signature_message(
            input_copy, tx.outputs[:], tx.locktime, tx_list_to_txo_list(tx_list)
        )
        hashed_msg = sha256_str_to_str(sha256_str_to_str(msg))
        # print("hashed message", hashed_msg)
        # print("script:", script)
        if not run_script(script, hashed_msg):
            return False
    return True


def check_sw_tx_validity(tx: Transaction, tx_list: list):
    return True
