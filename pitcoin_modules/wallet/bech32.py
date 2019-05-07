import codecs
import hashlib
import binascii

chars32 = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def convertbits(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret


def bech32_polymod(values):
    """Internal function that computes the Bech32 checksum."""
    generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def bech32_hrp_expand(hrp):
    """Expand the HRP into values for checksum computation."""
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def bech32_create_checksum(hrp, data):
    """Compute the checksum values given HRP and data."""
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]


def bech32_verify_checksum(hrp, data):
    """Verify a checksum given HRP and converted data characters."""
    return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1


def get_bech32_address(compressed_public_key: bytes, hrp):
    pubkey_sha_encrypted = hashlib.sha256(binascii.unhexlify(compressed_public_key)).hexdigest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(binascii.unhexlify(pubkey_sha_encrypted))
    pubkey_sha_ripemd_encrypted = binascii.unhexlify(ripemd160.hexdigest())
    print(binascii.hexlify(pubkey_sha_ripemd_encrypted))
    converted = [0] + convertbits(list(pubkey_sha_ripemd_encrypted), 8, 5)

    checksum = bech32_create_checksum(hrp, converted)

    data = converted + checksum
    string_data = ""
    for value in data:
        string_data += chars32[value]
    return hrp + '1' + string_data


def get_bech32_address_from_hashed_pubkey(pubkey, hrp='tb'):
    converted = [0] + convertbits(list(binascii.unhexlify(pubkey)), 8, 5)

    checksum = bech32_create_checksum(hrp, converted)

    data = converted + checksum
    string_data = ""
    for value in data:
        string_data += chars32[value]
    return hrp + '1' + string_data
