import unittest
from pitcoin_modules.settings import *
from pitcoin_modules.storage_handlers.utxo_pool import UTXOStorage
from pitcoin_modules.transaction import Transaction, Input, Output
from pitcoin_modules.blockchain.address_balance import get_balance


class TestAddressBalance(unittest.TestCase):
    storage_filepath = PROJECT_ROOT + "/storage/.utxo_pool_test.txt"

    def test_address_balance_simple(self):
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

        balance = get_balance(outp_list)
        self.assertEqual(900, balance)
