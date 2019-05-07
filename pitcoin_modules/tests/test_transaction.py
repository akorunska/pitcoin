import unittest
from pitcoin_modules.transaction import *
from pitcoin_modules.transaction.input import Input
from pitcoin_modules.transaction.output import Output


class TestReverceBytes(unittest.TestCase):
    def test_simple_number(self):
        s = "00000001"
        self.assertEqual("01000000", reverse_bytes(s))

    def test_usual_string(self):
        s = "ab2301a1"
        self.assertEqual("a10123ab", reverse_bytes(s))


class TestRawTransaction(unittest.TestCase):
    def test_raw_transaction_creation(self):
        inputs = [Input(
            "fc9e4f9c334d55c1dc535bd691a1c159b0f7314c54745522257a905e18a56779",
            1,
            "47304402206a2eb16b7b92051d0fa38c133e67684ed064effada1d7f925c842da401d4f22702201f196b10e6e4b4a9fff948e5c5d71ec5da53e90529c8dbd122bff2b1d21dc8a90121039b7bcd0824b9a9164f7ba098408e63e5b7e3cf90835cceb19868f54f8961a825"
        )]
        outputs = [Output(
            2207563,
            "76a914db4d1141d0048b1ed15839d0b7a4c488cd368b0e88ac"
        )]
        tx = Transaction(inputs, outputs, locktime=0)

        raw_tx = "01000000017967a5185e907a25225574544c31f7b059c1a191d65b53dcc1554d339c4f9efc010000006a47304402206a2eb16b7b92051d0fa38c133e67684ed064effada1d7f925c842da401d4f22702201f196b10e6e4b4a9fff948e5c5d71ec5da53e90529c8dbd122bff2b1d21dc8a90121039b7bcd0824b9a9164f7ba098408e63e5b7e3cf90835cceb19868f54f8961a825ffffffff014baf2100000000001976a914db4d1141d0048b1ed15839d0b7a4c488cd368b0e88ac00000000"
        self.assertEqual(raw_tx, Serializer.serialize_transaction(tx))

    def test_deserializing_raw_transaction(self):
        raw_tx = "01000000017967a5185e907a25225574544c31f7b059c1a191d65b53dcc1554d339c4f9efc010000006a47304402206a2eb16b7b92051d0fa38c133e67684ed064effada1d7f925c842da401d4f22702201f196b10e6e4b4a9fff948e5c5d71ec5da53e90529c8dbd122bff2b1d21dc8a90121039b7bcd0824b9a9164f7ba098408e63e5b7e3cf90835cceb19868f54f8961a825ffffffff014baf2100000000001976a914db4d1141d0048b1ed15839d0b7a4c488cd368b0e88ac00000000"
        deserialized = Deserializer.deserialize_transaction(raw_tx)

        inputs = [Input(
            "fc9e4f9c334d55c1dc535bd691a1c159b0f7314c54745522257a905e18a56779",
            1,
            "47304402206a2eb16b7b92051d0fa38c133e67684ed064effada1d7f925c842da401d4f22702201f196b10e6e4b4a9fff948e5c5d71ec5da53e90529c8dbd122bff2b1d21dc8a90121039b7bcd0824b9a9164f7ba098408e63e5b7e3cf90835cceb19868f54f8961a825"
        )]
        outputs = [Output(
            2207563,
            "76a914db4d1141d0048b1ed15839d0b7a4c488cd368b0e88ac"
        )]
        tx = Transaction(inputs, outputs, locktime=0)
        self.assertEqual(tx, deserialized)

    def test_raw_coinbase_transaction_creation(self):
        coinbase_tx = CoinbaseTransaction("76a914bfd3ebb5485b49a6cf1657824623ead693b5a45888ac", 2, 50, "")
        raw_tx = "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000002ffffffff0200f2052a010000001976a914bfd3ebb5485b49a6cf1657824623ead693b5a45888ac0000000000000000026a0000000000"
        self.assertEqual(raw_tx, Serializer.serialize_transaction(coinbase_tx))

    def test_deserializing_raw_coinbase_transaction(self):
        coinbase_tx = CoinbaseTransaction("76a914bfd3ebb5485b49a6cf1657824623ead693b5a45888ac", 2, 50, "")
        raw_tx = "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000002ffffffff0200f2052a010000001976a914bfd3ebb5485b49a6cf1657824623ead693b5a45888ac0000000000000000026a0000000000"
        self.assertEqual(coinbase_tx, Deserializer.deserialize_transaction(raw_tx))

    def test_wtxid_for_sw_transaction(self):
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

        self.assertNotEqual(tx.txid, tx.wtxid)

    def test_wtxid_for_nonsw_transaction(self):
        inputs = [Input(
            "fc9e4f9c334d55c1dc535bd691a1c159b0f7314c54745522257a905e18a56779",
            1,
            "47304402206a2eb16b7b92051d0fa38c133e67684ed064effada1d7f925c842da401d4f22702201f196b10e6e4b4a9fff948e5c5d71ec5da53e90529c8dbd122bff2b1d21dc8a90121039b7bcd0824b9a9164f7ba098408e63e5b7e3cf90835cceb19868f54f8961a825"
        )]
        outputs = [Output(
            2207563,
            "76a914db4d1141d0048b1ed15839d0b7a4c488cd368b0e88ac"
        )]
        tx = Transaction(inputs, outputs, locktime=0)

        self.assertEqual(tx.txid, tx.wtxid)

