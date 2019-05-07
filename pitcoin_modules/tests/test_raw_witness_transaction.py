import unittest
from pitcoin_modules.transaction import Transaction, Serializer, Deserializer, Output, Input
from pitcoin_modules.wallet import construct_witness_transaction


class TestRawWitnessTransaction(unittest.TestCase):
    def test_raw_transaction_creation(self):
        inputs = [Input(
            "fc9e4f9c334d55c1dc535bd691a1c159b0f7314c54745522257a905e18a56779",
            1,
            ""
        )]
        outputs = [Output(
            2207563,
            "0014db4d1141d0048b1ed15839d0b7a4c488cd368b0e"
        )]
        witness = ["47304402206a2eb16b7b92051d0fa38c133e67684ed064effada1d7f925c842da401d4f22702201f196b10e6e4b4a9fff948e5c5d71ec5da53e90529c8dbd122bff2b1d21dc8a90121039b7bcd0824b9a9164f7ba098408e63e5b7e3cf90835cceb19868f54f8961a825"]
        tx = Transaction(inputs, outputs, locktime=0, witness=witness, version=2)

        # raw_tx = "01000000017967a5185e907a25225574544c31f7b059c1a191d65b53dcc1554d339c4f9efc010000006a47304402206a2eb16b7b92051d0fa38c133e67684ed064effada1d7f925c842da401d4f22702201f196b10e6e4b4a9fff948e5c5d71ec5da53e90529c8dbd122bff2b1d21dc8a90121039b7bcd0824b9a9164f7ba098408e63e5b7e3cf90835cceb19868f54f8961a825ffffffff014baf2100000000001976a914db4d1141d0048b1ed15839d0b7a4c488cd368b0e88ac00000000"
        # self.assertEqual(raw_tx, Serializer.serialize_transaction(tx))
        print(Serializer.serialize_sw_transaction(tx))

    def test_forming_sw_transaction(self):
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

        formed_tx = construct_witness_transaction(sender_privkey, sender_address, recipient_address, 800, utxo_list)
        self.assertEqual(2, len(formed_tx.outputs))
        outp1 = formed_tx.outputs[0]
        outp2 = formed_tx.outputs[1]

        self.assertTrue(outp1.value + outp2.value <= 5000000000)
        self.assertEqual(800, outp1.value)
        self.assertEqual("0014c71afd5d2303c987ce8a4882ccb5c06636aaa224", outp1.scriptpubkey)

        self.assertEqual(1, len(formed_tx.witness))
        self.assertEqual("", formed_tx.inputs[0].scriptsig)

    def test_deserialize_sw_transaction(self):
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

        formed_tx = construct_witness_transaction(sender_privkey, sender_address, recipient_address, 800, utxo_list)
        serialized = Serializer.serialize_sw_transaction(formed_tx)

        self.assertEqual(formed_tx, Deserializer.deserialize_transaction(serialized))

    def test_forming_sw_transaction_with_bech32_recipient_address(self):
        sender_privkey = "936abdc0429eb4b38a045fcb8f531ff7cf3888c3a83797df5d033106c4ea6a20"
        sender_address = "1NERjvtBxL5ErAKhCC3mfgWbp3QMd8y6ba"
        recipient_address = "tb1qtpjzz4h24ghxxvc79c99vln7ycwe8stldvz9v6"

        utxo_list = [
            Output(
                5000000000,
                "76a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac",
                txid="07c0efe33946c5f81b5a86d79eda89e47979d4796d5ec675a9fccde7c31c4f50",
                vout=1
            )
        ]

        formed_tx = construct_witness_transaction(sender_privkey, sender_address, recipient_address, 800, utxo_list)
        self.assertEqual(2, len(formed_tx.outputs))
        outp1 = formed_tx.outputs[0]
        outp2 = formed_tx.outputs[1]

        self.assertTrue(outp1.value + outp2.value <= 5000000000)
        self.assertEqual(800, outp1.value)

        self.assertEqual(1, len(formed_tx.witness))
        self.assertEqual("", formed_tx.inputs[0].scriptsig)

