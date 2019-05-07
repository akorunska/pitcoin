import json
import unittest
from pitcoin_modules.settings import *
from pitcoin_modules.block import Block
from pitcoin_modules.storage_handlers.blockchain_meta import BlockchainMetaStorage


class TestBlockchainMeta(unittest.TestCase):
    storage_filepath = PROJECT_ROOT + "/storage/.blockchain_meta_test.txt"

    def test_difficulty_recalculation_works(self):
        storage = BlockchainMetaStorage(self.storage_filepath)
        storage.fill_storage_with_default_data()

        block_list = [
            Block(
                "1549643265",
                "00905ae710fe1fed3d07192937c908e89988038baee05ecec28780ebcac88a83",
                [
                    "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000000ffffffff0100f2052a010000001976a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac00000000"
                ]
            ),
            Block(
                "1549643285",
                "0003eb64ffaebce0832d0b097791b1c7e4c926cc505bf98308c2d8c8fd5c87b8",
                [
                    "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000000ffffffff0100f2052a010000001976a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac00000000"
                ]
            ),
            Block(
                "1549643371",
                "0000f4de2a720701953a5b2dfb4e18fbdbadb2b3a15f17a36ea4823acb69ef9b",
                [
                    "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000000ffffffff0100f2052a010000001976a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac00000000"
                ]
            )
        ]

        old_meta = storage.get_meta()
        storage.recalculate_difficulty(block_list)
        meta = storage.get_meta()
        self.assertNotEqual(old_meta['current_target'], meta['current_target'])


