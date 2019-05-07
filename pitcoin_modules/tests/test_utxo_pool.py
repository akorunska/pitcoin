import unittest
from pitcoin_modules.settings import *
from pitcoin_modules.transaction import Transaction, Input, Output
from pitcoin_modules.storage_handlers.utxo_pool import UTXOStorage


class TestUTXOPool(unittest.TestCase):
    storage_filepath = PROJECT_ROOT + "/storage/.utxo_pool_test.txt"

    def test_updating_utxo_pool_with_tx(self):
        storage = UTXOStorage(self.storage_filepath)
        storage.delete_all_otputs()

        outp0 = Output("", 10, txid="07c0efe33946c5f81b5a86d79eda89e47979d4796d5ec675a9fccde7c31c4f50", vout=1)
        storage.add_new_output(outp0)

        outp1 = Output(
                    900,
                    "76a914cabf271134a5f9228132598c8b4e6ad4586532f888ac",
                    txid="1423215db125380dd21051c0d22f31fd4be2a25794b8789796343f4015c1baff",
                    vout=1
                )
        outp2 = Output(
                    4999999100,
                    "76a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac",
                    txid="1423215db125380dd21051c0d22f31fd4be2a25794b8789796343f4015c1baff",
                    vout=2
                )

        tx = Transaction(
            [
                Input(
                    "07c0efe33946c5f81b5a86d79eda89e47979d4796d5ec675a9fccde7c31c4f50",
                    1,
                    "404bb493aa8509356c1295c65acd3a44c339729d865422a47cb15631cda545ee3fc2eb86b418a5bb90202040430b723fdbf8429ff232bfa521c25da09539644093410450e829ca678c60031a11b990fea865e03ba35d0579aa62750b918b98c4b935d803ecc57a4bb2fc2ab1193a87fca5386d71516aca89df267fc907bcb3b84d396a"
                )
            ],
            [outp1, outp2],
            0
        )

        storage.update_with_new_transaction(tx)

        outp_list = storage.get_all_outputs()
        self.assertFalse(outp0 in outp_list)
        self.assertTrue(outp1 in outp_list)
        self.assertTrue(outp2 in outp_list)

    def test_contains(self):
        storage = UTXOStorage(self.storage_filepath)
        storage.delete_all_otputs()

        outp0 = Output("", 10, txid="07c0efe33946c5f81b5a86d79eda89e47979d4796d5ec675a9fccde7c31c4f50", vout=1)

        self.assertFalse(storage.contains_output(outp0))
        storage.add_new_output(outp0)
        self.assertTrue(storage.contains_output(outp0))

    def test_get_all_unspent_outputs_for_address(self):
        storage = UTXOStorage(self.storage_filepath)
        storage.delete_all_otputs()

        outp1 = Output(
                    900,
                    "76a914cabf271134a5f9228132598c8b4e6ad4586532f888ac",
                    txid="1423215db125380dd21051c0d22f31fd4be2a25794b8789796343f4015c1baff",
                    vout=1
                )
        outp2 = Output(
                    4999999100,
                    "76a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac",
                    txid="1423215db125380dd21051c0d22f31fd4be2a25794b8789796343f4015c1baff",
                    vout=2
                )
        storage.add_new_output(outp1)
        storage.add_new_output(outp2)

        outp_list = storage.get_all_unspent_outputs_for_address("1KV2VGQiTB1B5KPEyyEPvifcqfS6PUxdxj")
        self.assertTrue(outp1 in outp_list)
        self.assertFalse(outp2 in outp_list)
