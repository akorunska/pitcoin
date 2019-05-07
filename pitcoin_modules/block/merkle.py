import hashlib
import codecs
from pitcoin_modules.wallet.wallet import sha256_bytes_to_bytes

def get_two_elements(data: list):
    el1 = data[0]
    del(data[0])
    if len(data) == 0:
        return el1, el1
    el2 = data[0]
    del(data[0])
    return el1, el2


def get_merkle_root(data: list):
    data = [codecs.encode(tx) for tx in data]
    if len(data) >= 2:
        current_list = data
    else:
        current_list = data * 2
    while len(current_list) > 1:
        next_list = []
        while len(current_list) > 0:
            el1, el2 = get_two_elements(current_list)
            hash_of_concatination = sha256_bytes_to_bytes(el1 + el2)
            next_list.append(hash_of_concatination)
        current_list = next_list
    return current_list[0]

