import json

from pitcoin_modules.transaction.input import Input
from pitcoin_modules.transaction.output import Output
from pitcoin_modules.wallet import *
from pitcoin_modules.settings import *


class Transaction:
    def __init__(self, inputs: list, outputs: list, locktime: int, witness=[], version=1):
        self.version = version
        self.inputs = inputs
        self.outputs = outputs
        self.locktime = locktime
        self.witness = []
        self.txid = self.get_hash()
        self.witness = witness
        self.wtxid = self.get_hash()

    def get_hash(self):
        tx_data = Serializer.serialize_transaction(self)
        return sha256_str_to_str(sha256_str_to_str(tx_data))

    def __str__(self):
        return self.to_json()

    def to_dict(self):
        data = {
            "version": self.version,
            "inputs": [input.__dict__ for input in self.inputs],
            "outputs": [output.__dict__ for output in self.outputs],
            "locktime": self.locktime,
            "txid": self.txid,
            "witness": self.witness,
            "wtxid": self.wtxid
        }
        for i, output in zip(range(1, len(data['outputs']) + 1), data['outputs']):
            output['txid'] = self.txid
            output['vout'] = i
        return data

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(dict):
        version = dict['version']
        inputs = [Input(input['txid'], input['vout'], input['scriptsig']) for input in dict['inputs']]
        outputs = [Output(output['value'], output['scriptpubkey']) for output in dict['outputs']]
        witness = [wint for wint in dict['witness']]
        return Transaction(inputs, outputs, dict['locktime'], version=version, witness=witness)

    def __eq__(self, other):
        return self.txid == other.txid


class CoinbaseTransaction(Transaction):
    def __init__(self, scriptpubkey, block_height: int, reward, wtx_merkle_root):
        inputs = []
        inputs.append(Input("0" * 64, int("f" * 8, 16), "%016x" % block_height))
        outputs = [
            Output(int(reward * 10**8), scriptpubkey),
            Output(0, "6a%02x%s" % (len(wtx_merkle_root) * 2, wtx_merkle_root))
        ]
        super().__init__(inputs, outputs, 0)


def reverse_bytes(s: str):
    res = list(s)
    for i in range(len(s) // 2):
        res[2*i] = s[len(s) - 2 - i*2]
        res[2*i + 1] = s[len(s) - 1 - i*2]
    return ''.join(res)


class Serializer:
    @staticmethod
    def serialize_transaction(tx: Transaction):
        if tx.version == 2:
            return Serializer.serialize_sw_transaction(tx)
        result = ""

        #packing tx version
        result += reverse_bytes("%08x" % tx.version)

        #packing tx inputs
        result += "%02x" % len(tx.inputs)
        #packing each input
        for input in tx.inputs:
            #pack txid
            result += reverse_bytes(input.txid)
            #pack vout
            result += reverse_bytes("%08x" % input.vout)
            #pack scriptsig
            result += "%02x" % (len(input.scriptsig) // 2)
            result += input.scriptsig
            #add sequence
            result += "f" * 8

        #packing tx outputs
        result += "%02x" % len(tx.outputs)
        # packing each output
        for output in tx.outputs:
            #pack value
            result += reverse_bytes("%016x" % output.value)
            # pack scriptsig
            result += "%02x" % (len(output.scriptpubkey) // 2)
            result += output.scriptpubkey

        #packing locktime
        result += reverse_bytes("%08x" % tx.locktime)
        return result

    @staticmethod
    def serialize_sw_transaction(tx: Transaction):
        result = ""

        # packing tx version
        result += reverse_bytes("%08x" % tx.version)

        # packing flag and marker
        result += "%02x%02x" % (0, 1)

        # packing tx inputs
        result += "%02x" % len(tx.inputs)
        # packing each input
        for input in tx.inputs:
            # pack txid
            result += reverse_bytes(input.txid)
            # pack vout
            result += reverse_bytes("%08x" % input.vout)
            # pack scriptsig
            result += "%02x" % (len(input.scriptsig) // 2)
            result += input.scriptsig
            # add sequence
            result += "f" * 8

        # packing tx outputs
        result += "%02x" % len(tx.outputs)
        # packing each output
        for output in tx.outputs:
            # pack value
            result += reverse_bytes("%016x" % output.value)
            # pack scriptsig
            result += "%02x" % (len(output.scriptpubkey) // 2)
            result += output.scriptpubkey

        # packing witness data
        result += "%02x" % len(tx.witness)
        for witn in tx.witness:
            # todo it is possibly nessesary to incude amount of stack elements of each witness
            # like this: result += "%02x" % 2 (2 elements in witness -- signature and pubkey

            # pack witness data
            result += "%02x" % (len(witn) // 2)
            result += witn

        # packing locktime
        result += reverse_bytes("%08x" % tx.locktime)
        return result

    @staticmethod
    def construct_tx_data_as_signature_message(inputs, outputs, locktime, utxo_list):
        for input in inputs:
            prev_txid = input.txid
            prev_vout = input.vout
            output_to_spend = None
            for utxo in utxo_list:
                if utxo.txid == prev_txid and utxo.vout == prev_vout:
                    output_to_spend = utxo
                    break
            input.scriptsig = output_to_spend.scriptpubkey
        return Serializer.serialize_transaction(Transaction(inputs, outputs, locktime))


class Deserializer:
    @staticmethod
    def deserialize_transaction(stx: str):
        cur = 0
        version = int(reverse_bytes(stx[cur:cur + 8]), 16)
        if version == 2:
            return Deserializer.deserialize_sw_transaction(stx)
        cur += 8

        inputs_count = int(stx[cur:cur + 2], 16)
        cur += 2
        inputs = []
        for i in range(inputs_count):
            txid = reverse_bytes(stx[cur:cur + 64])
            cur += 64
            vout = int(reverse_bytes(stx[cur:cur+8]), 16)
            cur += 8
            len = int(stx[cur:cur+2], 16)
            cur += 2
            scriptsig = stx[cur:cur + len*2]
            cur += len*2
            cur += 8    #skipping sequence

            inputs.append(Input(txid, vout, scriptsig))

        outputs_count = int(stx[cur:cur + 2], 16)
        cur += 2
        outputs = []
        for i in range(outputs_count):
            value = int(reverse_bytes(stx[cur:cur+16]), 16)
            cur += 16
            len = int(stx[cur:cur + 2], 16)
            cur += 2
            scriptpubkey = stx[cur:cur + len*2]
            cur += len*2

            outputs.append(Output(value, scriptpubkey))

        locktime = int(reverse_bytes(stx[cur:cur + 8]), 16)
        return Transaction(inputs, outputs, locktime)

    @staticmethod
    def deserialize_sw_transaction(stx: str):
        cur = 0
        version = int(reverse_bytes(stx[cur:cur + 8]), 16)
        cur += 8

        cur += 4

        inputs_count = int(stx[cur:cur + 2], 16)
        cur += 2
        inputs = []
        for i in range(inputs_count):
            txid = reverse_bytes(stx[cur:cur + 64])
            cur += 64
            vout = int(reverse_bytes(stx[cur:cur + 8]), 16)
            cur += 8
            len = int(stx[cur:cur + 2], 16)
            cur += 2
            scriptsig = stx[cur:cur + len * 2]
            cur += len * 2
            cur += 8  # skipping sequence

            inputs.append(Input(txid, vout, scriptsig))

        outputs_count = int(stx[cur:cur + 2], 16)
        cur += 2
        outputs = []
        for i in range(outputs_count):
            value = int(reverse_bytes(stx[cur:cur + 16]), 16)
            cur += 16
            len = int(stx[cur:cur + 2], 16)
            cur += 2
            scriptpubkey = stx[cur:cur + len * 2]
            cur += len * 2

            outputs.append(Output(value, scriptpubkey))

        witness_count = int(stx[cur:cur + 2], 16)
        cur += 2
        witness = []
        for i in range(witness_count):
            len = int(stx[cur:cur + 2], 16)
            cur += 2
            wit = stx[cur:cur + len * 2]
            cur += len * 2

            witness.append(wit)

        locktime = int(reverse_bytes(stx[cur:cur + 8]), 16)
        return Transaction(inputs, outputs, locktime, version=version, witness=witness)
