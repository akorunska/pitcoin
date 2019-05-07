import unittest

from pitcoin_modules import Deserializer
from pitcoin_modules.wallet import *
from pitcoin_modules.transaction import check_tx_validity


class TestConstructTransactionLockingScript(unittest.TestCase):
    def test_basic_construction(self):
        address = "1GFfoqR4Z4BZEy75Nd9CRMTKAev3oukY2Q"
        script = construct_transaction_locking_script(address)
        self.assertEqual("76a914a7501ae704b299ca3eb5bec10f8e3d8c3bb5cae088ac", script)

    def test_forming_transaction(self):
        sender_privkey = "936abdc0429eb4b38a045fcb8f531ff7cf3888c3a83797df5d033106c4ea6a20"
        sender_address = "1NERjvtBxL5ErAKhCC3mfgWbp3QMd8y6ba"
        recipient_address = "1K9moTCMoSrA9bNdYTgMt6ac1nim83xScU"

        utxo_list = [
            Output(
                5000000000,
                "76a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac",
                txid="07c0efe33946c5f81b5a86d79eda89e47979d4796d5ec675a9fccde7c31c4f50",
                vout=1
            )
        ]

        formed_tx = construct_transaction(sender_privkey, sender_address, recipient_address, 800, utxo_list)

        self.assertEqual(2, len(formed_tx.outputs))
        outp1 = formed_tx.outputs[0]
        outp2 = formed_tx.outputs[1]

        self.assertTrue(outp1.value + outp2.value <= 5000000000)
        self.assertEqual(800, outp1.value)

        self.assertEqual(1, len(formed_tx.inputs))
        inp = formed_tx.inputs[0]
        self.assertEqual("07c0efe33946c5f81b5a86d79eda89e47979d4796d5ec675a9fccde7c31c4f50", inp.txid)
        self.assertEqual(1, inp.vout)

    def test_formed_tx_is_valid(self):
        sender_privkey = "936abdc0429eb4b38a045fcb8f531ff7cf3888c3a83797df5d033106c4ea6a20"
        sender_address = "1NERjvtBxL5ErAKhCC3mfgWbp3QMd8y6ba"
        recipient_address = "1K9moTCMoSrA9bNdYTgMt6ac1nim83xScU"
        prev_tx = Deserializer.deserialize_transaction(
            "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000000ffffffff0100f2052a010000001976a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac00000000"
        )

        utxo_list = [
            Output(
                5000000000,
                "76a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac",
                txid="07c0efe33946c5f81b5a86d79eda89e47979d4796d5ec675a9fccde7c31c4f50",
                vout=1
            )
        ]

        formed_tx = construct_transaction(sender_privkey, sender_address, recipient_address, 800, utxo_list)

        self.assertTrue(check_tx_validity(formed_tx, [prev_tx]))

