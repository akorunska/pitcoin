import unittest
from pitcoin_modules.storage_handlers.chain import BlocksStorage
from pitcoin_modules.settings import *
from pitcoin_modules.block import Block


class TestPendingPool(unittest.TestCase):

    storage_filepath = PROJECT_ROOT + "/storage/.blocks_test.txt"

    def test_adding_to_mempool(self):
        storage = BlocksStorage(self.storage_filepath)
        storage.delete_all_blocks_from_mempool()

        bl = Block(
            "1549261064",
            "00b6e2b6784a067bdb5f19a1f9347cc3c6277d36e2fd2e164acd10e6e9eb5e86",
            [
            "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000000ffffffff0100f2052a010000001976a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac00000000"
            ]
        )
        bl.nonce = 438
        bl.hash_value = bl.get_hash()

        storage.add_block_to_storage(bl)

        bl_list = storage.get_all_blocks()
        self.assertTrue(str(bl) in [str(b) for b in bl_list])

    def test_get_chain_length(self):
        storage = BlocksStorage(self.storage_filepath)
        storage.delete_all_blocks_from_mempool()

        bl = Block(
            "1549261064",
            "0000000000000000000000000000000000000000000000000000000000000000",
            [
                "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000000ffffffff0100f2052a010000001976a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac00000000"
            ]
        )
        bl.nonce = 438
        bl.hash_value = bl.get_hash()

        bl_list = storage.get_all_blocks()
        self.assertEqual(0, len(bl_list))

        storage.add_block_to_storage(bl)

        bl_list = storage.get_all_blocks()
        self.assertEqual(1, len(bl_list))

    def test_adding_valid_new_block(self):
        storage = BlocksStorage(self.storage_filepath)
        storage.delete_all_blocks_from_mempool()

        bl = Block(
            "1549261064",
            "0000000000000000000000000000000000000000000000000000000000000000",
            [
                "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000000ffffffff0100f2052a010000001976a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac00000000"
            ]
        )
        bl.nonce = 438
        bl.hash_value = bl.get_hash()
        storage.add_block_to_storage(bl)

        new_block = Block(
            "1549263339",
            "9e054cafb0bad6950a05ab4fd27922f0a351ec09d2e9715b54819d4fcd489b17",
            [
                "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000001ffffffff0100f2052a010000001976a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac00000000"
            ]
        )
        new_block.nonce = 44
        new_block.hash_value = new_block.get_hash()

        bl_list = storage.get_all_blocks()
        self.assertEqual(1, len(bl_list))

        storage.add_block_to_storage(new_block)

        bl_list = storage.get_all_blocks()
        self.assertEqual(2, len(bl_list))
        self.assertTrue(str(new_block) in [str(b) for b in bl_list])

        def test_adding_invalid_new_block(self):
            storage = BlocksStorage(self.storage_filepath)
            storage.delete_all_blocks_from_mempool()

            bl = Block(
                "1549261064",
                "0000000000000000000000000000000000000000000000000000000000000000",
                [
                    "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000000ffffffff0100f2052a010000001976a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac00000000"
                ]
            )
            bl.nonce = 438
            bl.hash_value = bl.get_hash()
            storage.add_block_to_storage(bl)

            new_block = Block(
                "1549263339",
                "00b6e2b6784a067bdb5f19a1f9347cc3c6277d3689fd2e164acd10e6e9eb5e86",
                [
                    "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000001ffffffff0100f2052a010000001976a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac00000000"
                ]
            )
            new_block.nonce = 44
            new_block.hash_value = new_block.get_hash()

            bl_list = storage.get_all_blocks()
            self.assertEqual(1, len(bl_list))

            storage.add_block_to_storage(new_block)

            bl_list = storage.get_all_blocks()
            self.assertEqual(1, len(bl_list))
            self.assertFalse(str(new_block) in [str(b) for b in bl_list])

