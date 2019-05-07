import unittest
from pitcoin_modules.script import *


class TestScript(unittest.TestCase):
    def test_script_correct(self):
        s = "4045a5ed6b890c5e48a81c0a7caf4d19df522eb4d91edd9e8cfdd2ab620ff21eaaf872d96e12abceed2be565dd0f06a2eeda72cc533e2a7b7b01917600cdcf5346410450e829ca678c60031a11b990fea865e03ba35d0579aa62750b918b98c4b935d803ecc57a4bb2fc2ab1193a87fca5386d71516aca89df267fc907bcb3b84d396a76a914e8e4b375038b0a1a1dc70543eab7ea6ce279df4388ac"
        self.assertTrue(run_script(s, "867c0d41244dd07cd898246eeaa216ab4e5b3c47b949b32c94f5c3385392258c"))

