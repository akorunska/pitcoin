import math
import pickle
from pathlib import Path
from pitcoin_modules.settings import *


class BlockchainMetaStorage:
    def __init__(self, filepath=PROJECT_ROOT+'/storage/.blockchain_meta.txt'):
        self.storage_filepath = filepath

    def fill_storage_with_default_data(self):
        if not Path(self.storage_filepath).is_file():
            Path(self.storage_filepath).touch()
        blockchain_meta = {
            'original_target': '0x000a000000000000000000000000000000000000000000000000000000000000',
            'current_target': '0x00a0000000000000000000000000000000000000000000000000000000000000',
            'difficulty': int('f' * 64, 16) / int('0x000a000000000000000000000000000000000000000000000000000000000000', 16),
            'target_update_frequency': 3,   # every 3 blocks difficulty is going to be updated
            'halving_frequency': 5,
            'seconds_to_create_block_expected': 20,    # time in seconds to create each block for the network
            'current_miner_reward': 50,
            'total_supply': 21 * 10**6,
            'mined_pitcoins': 0
        }
        with open(self.storage_filepath, 'wb+') as fp:
            pickle.dump(blockchain_meta, fp)

    def get_meta(self):
        if not Path(self.storage_filepath).is_file():
            self.fill_storage_with_default_data()

        with open(self.storage_filepath, 'rb') as fp:
            try:
                blockchain_meta = pickle.load(fp)
            except EOFError:
                self.fill_storage_with_default_data()
                blockchain_meta = self.get_meta()

        return blockchain_meta

    def update_meta(self, new_meta):
        with open(self.storage_filepath, 'wb+') as fp:
            pickle.dump(new_meta, fp)

    def halving(self):
        meta = self.get_meta()
        if meta['mined_pitcoins'] == meta['total_supply']:
            meta['current_miner_reward'] = 0
        else:
            meta['current_miner_reward'] = meta['current_miner_reward'] / 2
        with open(self.storage_filepath, 'wb+') as fp:
            pickle.dump(meta, fp)

    def recalculate_difficulty(self, last_n_blocks):
        meta = self.get_meta()
        print(meta)

        total_creation_time = int(last_n_blocks[-1].timestamp) - int(last_n_blocks[0].timestamp)
        ideal_creation_time = meta['target_update_frequency'] * meta['seconds_to_create_block_expected']
        print(total_creation_time, ideal_creation_time)

        correcting_coefficient = ideal_creation_time / total_creation_time

        print(correcting_coefficient)
        if math.fabs(correcting_coefficient - 1) > 0.15:
            correcting_coefficient = 1 + math.copysign(0.15, correcting_coefficient - 1)
        print(correcting_coefficient)

        meta['difficulty'] = correcting_coefficient * meta['difficulty']

        print("cur target: ",  int((int('f' * 64, 16) / meta['difficulty'])))
        print("cur target in hex: ", "%064x" %  int((int('f' * 64, 16) / meta['difficulty'])))
        meta['current_target'] = "%064x" % int(int('f' * 64, 16) / meta['difficulty'])

        self.update_meta(meta)


