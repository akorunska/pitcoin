import codecs
from pitcoin_modules.block.block import Block
from pitcoin_modules.transaction import *


#outp_list contains only unspent outputs for the corresponding address
def get_balance(outp_list: list):
    balance = 0
    for outp in outp_list:
        balance += outp.value
    return balance
