import cmd
from pathlib import Path
from pitcoin_modules.wallet import *
from pitcoin_modules.transaction import *
from pitcoin_modules.settings import *
import requests
import json

# todo rewrite all functions to receive and return a string + add test coverage

class OptionsHandler:
    @staticmethod
    def handle_do_new_options(arg):
        result = {'compressed': False, 'save_address': False}
        args = arg.split()
        for arg in args:
            if arg == "-c":
                print("using compressed public key for address creation")
                result['compressed'] = True
            elif arg == "-a":
                print("created address is going to be saved in file")
                result["save_address"] = True
            else:
                print("unknown option:", arg)
        return result

    @staticmethod
    def handle_do_import_options(arg):
        result = {'compressed': False, 'save_address': False, 'args_valid': False}
        args = arg.split()
        result['filepath'] = args[0]
        for i in range(1, len(args)):
            if args[i] == "-c":
                print("using compressed public key for address creation")
                result['compressed'] = True
            elif args[i] == "-a":
                print("created address is going to be saved in file")
                result["save_address"] = True
            else:
                print("unknown option:", args[i])
        if not Path(result['filepath']).is_file():
            print(result['filepath'], "is not a file")
            return result
        result['args_valid'] = True
        return result

    @staticmethod
    def handle_do_remember_privkey_options(arg):
        result = {'privkey': ""}
        args = arg.split()
        if len(args[0]) == 64:
            result["privkey"] = args[0]
        else:
            print("seems like specified private key is not correct.")
        return result

    @staticmethod
    def handle_do_send_options(arg, privkey):
        result = {'recipient': "", 'address': "", 'amount': -1, 'args_valid': False}
        if privkey == "":
            print("please, specify your private key using <remember_privkey> command before calling send")
            return result
        args = arg.split()
        if len(args) != 2:
            print("wrong number of arguments")
            return result
        # todo check if recipient and sender addresses are valid
        result['recipient'] = args[0]
        result['amount'] = int(args[1])
        result['sender'] = read_file_contents('pitcoin_modules/address')
        if result['amount'] <= 0:
            print("amount specified is not positive integer")
            return result
        result['args_valid'] = True
        return result


class WalletCLI(cmd.Cmd):
    intro = 'Welcome to pitcoin wallet-cli. Type help or ? to list commands.\n'
    prompt = '\n(pitcoin-wallet-cli) '
    user_privkey = ""
    api_url = "http://" + API_HOST + ":" + API_PORT
    i = 0

    def do_new(self, arg):
        'Generate new private key and receive associated public key and address. \n' \
        'usage: <new -c -a> \n' \
        '-c: By default uncompressed public key is used. To use compressed public key type <new -c> \n' \
        '-a: Save created address to the file on the machine called address.'

        options = OptionsHandler.handle_do_new_options(arg)

        hex_private_key = generate_private_key()
        wif_private_key = convert_hex_private_key_to_wif(hex_private_key)
        self.hande_wallet_credentials_generation(options, hex_private_key, wif_private_key.decode("utf-8"))


    def do_swnew(self, arg):
        'Generate new private key and receive associated public key and address. \n' \
        'usage: <swnew -a> \n' \
        '-a: Save created address to the file on the machine called address.'

        options = OptionsHandler.handle_do_new_options(arg)

        hex_private_key = generate_private_key()
        wif_private_key = convert_hex_private_key_to_wif(hex_private_key)
        self.hande_swallet_credentials_generation(options, hex_private_key, wif_private_key.decode("utf-8"))


    def do_import(self, arg):
        'Import private key in WIF format and receive associated public key and address. \n' \
        'usage: <import path/to/file -c -a> \n' \
        '-c: By default uncompressed public key is used. To use compressed public key type <new -c> \n' \
        '-a: Save created address to the file on the machine called address.'
        options = OptionsHandler.handle_do_import_options(arg)
        if not options['args_valid']:
            return
        wif_private_key = read_file_contents(options['filepath'])
        # todo check if wif in the file is valid
        hex_private_key = convert_wif_to_hex_private_key(wif_private_key)
        self.hande_wallet_credentials_generation(options, hex_private_key.decode("utf-8"), wif_private_key)

    def do_swimport(self, arg):
        'Import private key in WIF format and receive associated public key and address. \n' \
        'usage: <swimport path/to/file  -a> \n' \
        '-a: Save created address to the file on the machine called address.'
        options = OptionsHandler.handle_do_import_options(arg)
        if not options['args_valid']:
            return
        wif_private_key = read_file_contents(options['filepath'])
        hex_private_key = convert_wif_to_hex_private_key(wif_private_key)
        self.hande_swallet_credentials_generation(options, hex_private_key.decode("utf-8"), wif_private_key)

    def do_remember_privkey(self, arg):
        'Command, that must be called before any send operation. ' \
        'Private key is stored in program memory and needs remembered every time wallet-cli is relauched \n' \
        'usage: <remember_privkey user_hex_privkey>'
        options = OptionsHandler.handle_do_remember_privkey_options(arg)
        self.user_privkey = options['privkey']

    def do_send(self, arg):
        'Send some pitcoins to another address\n' \
        'usage: <send recipient_address amount>'
        options = OptionsHandler.handle_do_send_options(arg, self.user_privkey)
        if not options['args_valid']:
            return
        # tx = Transaction(options['sender'], options['recipient'], options['amount'])
        # tx.sign_transaction(self.user_privkey)
        # serialized = Serializer.serialize_transaction(tx)
        # requests.post(self.api_url + '/transaction/new', serialized)
        if requests.get(self.api_url + '/balance?address=' + options['sender']).json()['balance'] < options['amount']:
            print("sender does not have enough pitcoins for this transaction")
            return
        utxo_list = requests.get(self.api_url + '/utxo?address=' + options['sender']).json()
        utxo_list = [Output(utxo['value'], utxo['scriptpubkey'], utxo['txid'], utxo['vout']) for utxo in utxo_list]
        tx = construct_transaction(self.user_privkey, options['sender'], options['recipient'], options['amount'], utxo_list)
        print(tx)
        print(Serializer.serialize_transaction(tx))

    def do_swsend(self, arg):
        'Send some pitcoins to another address\n' \
        'usage: <send recipient_address amount>'
        options = OptionsHandler.handle_do_send_options(arg, self.user_privkey)
        if not options['args_valid']:
            return
        # tx = Transaction(options['sender'], options['recipient'], options['amount'])
        # tx.sign_transaction(self.user_privkey)
        # serialized = Serializer.serialize_transaction(tx)
        # requests.post(self.api_url + '/transaction/new', serialized)
        if requests.get(self.api_url + '/balance?address=' + options['sender']).json()['balance'] < options['amount']:
            print("sender does not have enough pitcoins for this transaction")
            return
        utxo_list = requests.get(self.api_url + '/utxo?address=' + options['sender']).json()
        utxo_list = [Output(utxo['value'], utxo['scriptpubkey'], utxo['txid'], utxo['vout']) for utxo in utxo_list]
        tx = construct_witness_transaction(self.user_privkey, options['sender'], options['recipient'], options['amount'], utxo_list)
        print(tx)
        print(Serializer.serialize_sw_transaction(tx))

    def do_broadcast(self, arg):
        'Get balance of the address\n' \
        'usage: <broadcast raw_tx>'
        raw_tx = arg.strip()
        print(requests.post(self.api_url + '/transaction/new', raw_tx).json())

    def do_balance(self, arg):
        'Get balance of the address\n' \
        'usage: <balance address>'
        addr = arg.strip()
        resp = requests.get(self.api_url + '/balance?address=' + addr).json()
        print(resp['balance'])

    def do_quit(self, arg):
        'Exit wallet-cli shell'
        print('Thank you for using pitcoin-wallet-cli')
        return True

    # service static methods, containing repetative logic
    @staticmethod
    def hande_wallet_credentials_generation(options, hex_private_key, wif_private_key):
        public_key = get_public_key_from_private_key(hex_private_key, options['compressed'])
        address = get_address_from_private_key(hex_private_key, options['compressed'])

        WalletCLI.print_wallet_info(hex_private_key, wif_private_key, public_key.decode("utf-8"), address)
        if options["save_address"]:
            WalletCLI.save_address_to_file(address, "address")

    @staticmethod
    def hande_swallet_credentials_generation(options, hex_private_key, wif_private_key):
        public_key = get_public_key_from_private_key(hex_private_key, use_compressed=True)
        address = get_bech32_address(public_key, 'tb')

        WalletCLI.print_wallet_info(hex_private_key, wif_private_key, public_key.decode("utf-8"), address)
        if options["save_address"]:
            WalletCLI.save_address_to_file(address, "swaddress")

    @staticmethod
    def print_wallet_info(hex_private_key, wif_private_key, public_key, address):
        print("hex private key | ", hex_private_key)
        print("wif private key | ", wif_private_key)
        print("public key      | ", public_key)
        print("pitcoin address | ", address)

    @staticmethod
    def save_address_to_file(address, filename):
        file = open(PROJECT_ROOT + "/" + filename, "w")
        file.write(address)
        file.close()


if __name__ == '__main__':
    WalletCLI().cmdloop()

# remember_privkey 936abdc0429eb4b38a045fcb8f531ff7cf3888c3a83797df5d033106c4ea6a20
# swsend 1C8RSTSSY34XHwShUdk18SZmm7wqc1sLqD 30
# tb1qx5de2erumcw2w4kgzry6wcjewy86q248m78yqj