import unittest
import numpy as np
from pitcoin_modules.wallet import *


class TestGeneratePrivateKey(unittest.TestCase):
    def test_generated_key_length(self):
        for x in range(100):
            privkey = generate_private_key()
            self.assertEqual(64, len(privkey.encode("utf-8")))

    def test_generated_keys_are_unique(self):
        keys = []
        for x in range(100):
            keys.append(generate_private_key())
        self.assertEqual(len(keys), np.unique(keys).size)

    def test_generated_keys_value_does_not_exseed_order_of_elliptic_curve(self):
        order_of_elliptic_curve = 1.158 * 10 ** 77
        for x in range(100):
            privkey = generate_private_key()
            self.assertTrue(float(int(privkey, 16)) < order_of_elliptic_curve)


class TestConvertHexPrivateKeyToWif(unittest.TestCase):
    def test_correct_hex(self):
        hex = "c1421c809f270aa475f16adeaf3dab4fb9d28eaccbf2e1e35ff38cf99609c308"
        result = convert_hex_private_key_to_wif(hex)
        self.assertEqual(b"5KHQ6zJtnXr3P99stSh2e2VpwgQwbU5qsMDcJvqwXjQNSQGS6P2", result)

    def test_correct_hex_as_bytes(self):
        hex = "c1421c809f270aa475f16adeaf3dab4fb9d28eaccbf2e1e35ff38cf99609c308"
        result = convert_hex_private_key_to_wif(hex)
        self.assertEqual(b"5KHQ6zJtnXr3P99stSh2e2VpwgQwbU5qsMDcJvqwXjQNSQGS6P2", result)


class TestConvertWifPrivateKeyToHex(unittest.TestCase):
    def test_correct_wif(self):
        wif = "5KHQ6zJtnXr3P99stSh2e2VpwgQwbU5qsMDcJvqwXjQNSQGS6P2"
        result = convert_wif_to_hex_private_key(wif)
        self.assertEqual(b"c1421c809f270aa475f16adeaf3dab4fb9d28eaccbf2e1e35ff38cf99609c308", result)

    def test_correct_wif_as_bytes(self):
        wif = b"5KHQ6zJtnXr3P99stSh2e2VpwgQwbU5qsMDcJvqwXjQNSQGS6P2"
        result = convert_wif_to_hex_private_key(wif)
        self.assertEqual(b"c1421c809f270aa475f16adeaf3dab4fb9d28eaccbf2e1e35ff38cf99609c308", result)


class TestGetPublicKeyFromPrivateKey(unittest.TestCase):
    def test_uncompressed_public_key(self):
        privkey = "c1421c809f270aa475f16adeaf3dab4fb9d28eaccbf2e1e35ff38cf99609c308"
        pubk_uncompressed = b"04d6b50d095cf9200fe4b33fb43a7391cdeced7344c91ca9344a39b5d6ae00a3e0b9bb130ce85ec7a30c7bddefd4771c871b385044ab0d31218f86945f5bf10af3"
        result = get_public_key_from_private_key(privkey, use_compressed=False)
        self.assertEqual(pubk_uncompressed, result)

    def test_compressed_public_key_odd_y(self):
        privkey = "c1421c809f270aa475f16adeaf3dab4fb9d28eaccbf2e1e35ff38cf99609c308"
        pubk_compressed = b"03d6b50d095cf9200fe4b33fb43a7391cdeced7344c91ca9344a39b5d6ae00a3e0"
        result = get_public_key_from_private_key(privkey, use_compressed=True)
        self.assertEqual(pubk_compressed, result)

    def test_compressed_public_key_even_y(self):
        privkey = "621a7be3c725449822fab924774550ed0f1c3bfb66b52387be8635fc062144ca"
        pubk_compressed = b"02e1ee2984814b1ce373e21908b4dd0c89e10a0d88ae71c286ec3e1784f8f9ad0d"
        result = get_public_key_from_private_key(privkey, use_compressed=True)
        self.assertEqual(pubk_compressed, result)


class TestGetAddressFromPrivateKey(unittest.TestCase):
    def test_adress_from_uncompressed_pubkey(self):
        privkey = "c1421c809f270aa475f16adeaf3dab4fb9d28eaccbf2e1e35ff38cf99609c308"
        address = "1CARnkZGHSCcGUgvNQhvUMQa5WWTQCc28p"
        result = get_address_from_private_key(privkey, use_compressed=False)
        self.assertEqual(address, result)

    def test_adress_from_compressed_pubkey_odd_y(self):
        privkey = "c1421c809f270aa475f16adeaf3dab4fb9d28eaccbf2e1e35ff38cf99609c308"
        address = "1Pzc9Xn5B6VdtD9GkVs4qexJhLM551VXJV"
        result = get_address_from_private_key(privkey, use_compressed=True)
        self.assertEqual(address, result)

    def test_adress_from_compressed_pubkey_even_y(self):
        privkey = "621a7be3c725449822fab924774550ed0f1c3bfb66b52387be8635fc062144ca"
        address = "1P7qz3yNLMsMAQKX6JvoVqQHXgT5vAS8ur"
        result = get_address_from_private_key(privkey, use_compressed=True)
        self.assertEqual(address, result)


class TestGetBech32Address(unittest.TestCase):
    def test_basic_mainnet_bech32(self):
        compressed_pk = b'0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798'
        bech32 = get_bech32_address(compressed_pk, 'bc')
        self.assertEqual("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", bech32)

    def test_bech32_from_hashed_pubkey(self):
        compressed_pk = b'0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798'
        bech32 = get_bech32_address(compressed_pk, 'tb')
        self.assertEqual("tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx", bech32)
        self.assertEqual(bech32, get_bech32_address_from_hashed_pubkey("751e76e8199196d454941c45d1b3a323f1433bd6"))


class TestSingMessage(unittest.TestCase):
    def test_sing_and_check(self):
        privkey = "c1421c809f270aa475f16adeaf3dab4fb9d28eaccbf2e1e35ff38cf99609c308"
        message = b'the test message for signing'
        responce = sign_message_with_private_key(privkey, message)
        self.assertTrue(check_message_signature(responce['public_key'], responce['signature'], message))

