import errno
import os
import requests
from pitcoin_modules.blockchain import Blockchain
from pitcoin_modules.settings import *


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def clear_storage(path):
    try:
        os.remove(path + ".blocks.txt")
    except OSError:
        pass
    try:
        os.remove(path + ".mempool.txt")
    except OSError:
        pass
    try:
        os.remove(path + ".utxopool.txt")
    except OSError:
        pass
    try:
        os.remove(path + ".blockchain_meta.txt")
    except OSError:
        pass


def genesis_block_setup():
    genesis_block = blockchain.genesis_block()

    requests.post(api_url + '/chain/block', str(genesis_block))


def add_known_nodes():
    for node in TRUSTED_NODES:
        requests.post(api_url + '/node', node)
    for node in TRUSTED_NODES:
        requests.post(node + '/node', api_url)
    blockchain.resolve_conflicts()

api_url = "http://" + API_HOST + ":" + API_PORT

make_sure_path_exists('pitcoin_modules/storage/')
clear_storage('pitcoin_modules/storage/')

# get all known nodes from the settings file
# if there are no nodes, create own genesis block
blockchain = Blockchain()

if len(TRUSTED_NODES) > 0:
    add_known_nodes()
else:
    genesis_block_setup()
