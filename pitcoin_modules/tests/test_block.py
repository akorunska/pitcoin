import json
import unittest
from pitcoin_modules.block import Block


class TestBlock(unittest.TestCase):
    def test_json_serialize_deserialize(self):
        bl = Block(
            "1549261064",
            "00b6e2b6784a067bdb5f19a1f9347cc3c6277d36e2fd2e164acd10e6e9eb5e86",
            [
            "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff080000000000000000ffffffff0100f2052a010000001976a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac00000000"
            ]
        )

        json_string = str(bl)
        restored_block = Block.from_json(json.loads(json_string))
        self.assertEqual(bl.hash_value, restored_block.hash_value)
        self.assertEqual(str(bl), str(restored_block))

