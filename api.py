import requests
import json
from flask_restful import Resource, Api, reqparse
from flask import Flask, request

from pitcoin_modules.storage_handlers.pending_pool import MemPoolStorage
from pitcoin_modules.storage_handlers.chain import BlocksStorage
from pitcoin_modules.storage_handlers.utxo_pool import UTXOStorage
from pitcoin_modules.storage_handlers.blockchain_meta import BlockchainMetaStorage
from pitcoin_modules.settings import *
from pitcoin_modules.blockchain.address_balance import *
import logging


mempool = MemPoolStorage()
blocks = BlocksStorage()
utxo_pool = UTXOStorage()
blockchain_meta = BlockchainMetaStorage()
nodes = []

app = Flask(__name__)

# log = logging.getLogger('werkzeug')
# log.disabled = True
# app.logger.disabled = True

api = Api(app)


class Transaction(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('txid', type=str)
        args = parser.parse_args()

        if args['txid']:
            json_repr = json.dumps([tx.to_dict() for tx in blocks.get_transaction_by_txid(args['txid'])])
        else:
            json_repr = json.dumps([tx.to_dict() for tx in blocks.get_all_transactions_from_blocks()])
        response = app.response_class(
            response=json_repr,
            status=200,
            mimetype='application/json'
        )
        return response


class TransactionNew(Resource):
    def post(self):
        serialized_tx = codecs.decode(request.data)
        deserialized = Deserializer.deserialize_transaction(serialized_tx)
        if mempool.contains_transaction(deserialized):
            return

        transactions = blocks.get_all_transactions_from_blocks()
        response = app.response_class(
            response=json.dumps({
                "result": mempool.add_serialized_transaction_to_mempool(serialized_tx, transactions)
            }),
            status=200,
            mimetype='application/json'
        )

        #broadcasting transaction to all known nodes
        for node in nodes:
            requests.post(node + '/transaction/new', serialized_tx)

        return response


class TransactionPending(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', type=int)
        args = parser.parse_args()

        if args['amount'] == 3:
            list = mempool.get_three_first_transactions()
        else:
            list = mempool.get_all_transactions()
        response = app.response_class(
            response=json.dumps([tx.to_dict() for tx in list]),
            status=200,
            mimetype='application/json'
        )
        return response

    def delete(self):
        return mempool.delete_all_transactions_from_mempool()


class TransactionDeserialize(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('data', type=str, required=True)
        args = parser.parse_args()

        tx = Deserializer.deserialize_transaction(args['data'])
        response = app.response_class(
            response=json.dumps(tx.to_dict()),
            status=200,
            mimetype='application/json'
        )
        return response


class Chain(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('trunc', type=str)
        args = parser.parse_args()

        list = blocks.get_all_blocks()
        if args['trunc'] == "last":
            last = list[-1]
            json_repr = json.dumps(last.__dict__)
        else:
            json_repr = json.dumps([b.__dict__ for b in list])
        response = app.response_class(
            response=json_repr,
            status=200,
            mimetype='application/json'
        )
        return response

    def delete(self):
        response = app.response_class(
            response=json.dumps({"result": blocks.delete_all_blocks_from_mempool()}),
            status=200,
            mimetype='application/json'
        )
        return response


class ChainBlock(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('height', type=int)
        args = parser.parse_args()

        list = blocks.get_all_blocks()

        if args['height'] and args['height'] < len(list):
            block = list[args['height']]
        else:
            block = blocks.get_last_block()
        json_repr = json.dumps(block.__dict__)

        response = app.response_class(
            response=json_repr,
            status=200,
            mimetype='application/json'
        )
        return response

    def post(self):
        json_repr = json.loads(codecs.decode(request.data, 'ascii'))
        block = Block(
            json_repr['timestamp'],
            json_repr['previous_hash'],
            [tx for tx in json_repr['transactions']],
            json_repr['nonce']
        )

        last_block = blocks.get_last_block()
        if last_block:
            if block.hash_value == last_block.hash_value:
                return ""

        response = app.response_class(
            response=json.dumps({"result": blocks.add_block_to_storage(block)}),
            status=200,
            mimetype='application/json'
        )

        for tx in block.transactions:
            deserialized = Deserializer.deserialize_transaction(tx)
            # deleting all transactions that new block contains from the mempool
            mempool.delete_transaction_if_exists(deserialized)
            # update utxo pool with new transactions data
            utxo_pool.update_with_new_transaction(deserialized)

        meta = blockchain_meta.get_meta()

        # recalculate difficulty
        if len(blocks.get_all_blocks()) % meta['target_update_frequency'] == 0:
            bl_list = blocks.get_last_n_blocks(3)
            blockchain_meta.recalculate_difficulty(bl_list)

        # halving
        if len(blocks.get_all_blocks()) % meta['halving_frequency'] == 0:
            blockchain_meta.halving()

        # broadcasting new block for all known nodes
        for node in nodes:
            requests.post(node + '/chain/block', json.dumps(json_repr))

        return response


class ChainLength(Resource):
    def get(self):
        response = app.response_class(
            response=json.dumps({"chain_length": len(blocks.get_all_blocks())}),
            status=200,
            mimetype='application/json'
        )
        return response


class Node(Resource):
    def get(self):
        return app.response_class(
            response=json.dumps(nodes),
            status=200,
            mimetype='application/json'
        )

    def post(self):
        nodes.append(codecs.decode(request.data, 'ascii'))
        return True


class Balance(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('address', type=str, required=True)
        args = parser.parse_args()

        res = get_balance(utxo_pool.get_all_unspent_outputs_for_address(args['address']))
        return app.response_class(
            response=json.dumps({'balance': res}),
            status=200,
            mimetype='application/json'
        )


class UTXO(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('address', type=str)
        args = parser.parse_args()

        if args['address']:
            utxo_list = utxo_pool.get_all_unspent_outputs_for_address(args['address'])
        else:
            utxo_list = utxo_pool.get_all_outputs()
        return app.response_class(
            response=json.dumps([outp.__dict__ for outp in utxo_list]),
            status=200,
            mimetype='application/json'
        )

    def delete(self):
        response = app.response_class(
            response=json.dumps({"result": utxo_pool.delete_all_otputs()}),
            status=200,
            mimetype='application/json'
        )
        return response


class Meta(Resource):
    def get(self):
        return app.response_class(
            response=json.dumps(blockchain_meta.get_meta()),
            status=200,
            mimetype='application/json'
        )


api.add_resource(Transaction, '/transaction/', methods=['GET'])
api.add_resource(TransactionNew, '/transaction/new', methods=['POST'])
api.add_resource(TransactionPending, '/transaction/pendings', methods=['GET', 'DELETE'])
api.add_resource(TransactionDeserialize, '/transaction/deserialize', methods=['GET'])
api.add_resource(Chain, '/chain', methods=['GET', 'DELETE'])
api.add_resource(ChainBlock, '/chain/block', methods=['GET', 'POST'])
api.add_resource(ChainLength, '/chain/length', methods=['GET'])
api.add_resource(Node, '/node', methods=['GET', 'POST'])
api.add_resource(Balance, '/balance', methods=['GET'])
api.add_resource(UTXO, '/utxo', methods=['GET'])
api.add_resource(Meta, '/meta', methods=['GET'])


if __name__ == '__main__':
    app.run(host=API_HOST, port=API_PORT)
