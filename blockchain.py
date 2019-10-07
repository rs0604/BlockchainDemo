# coding: UTF-8

import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # ジェネシスブロックを作る
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        ブロックチェーンに新しいブロックを作る
        :param proof: <int> プルーフ・オブ・ワークアルゴリズムから得られるプルーフ
        :param previous_hash: オプション <str> 前のブロックのハッシュ
        :return: <dict> 新しいブロック
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # 現在のトランザクションリストをリセット
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        次に採掘されるブロックに加える新しいトランザクションを作る
        :param sender: <str> 送信者のアドレス
        :param recipient: <str> 受信者のアドレス
        :param amount: <int> 量
        :return: <int> このトランザクションを含むブロックのアドレス
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        ブロックの SHA-256 ハッシュを作る
        :param block: <dict> ブロック
        :return: <str>
        """

        # 必ずDictionaryがソートされている必要がある。
        # そうでないと、一貫性のないハッシュとなってしまう。
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        シンプルなプルーフ・オブ・ワークのアルゴリズム:
         - hash(pp') の最初の4つが0となるような p' を探す
         - p は1つ前のブロックのプルーフ、p'は新しいブロックのプルーフ
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        プルーフが正しいか確認する: hash(last_proof, proof)の最初の4つが0となっているか？
        :param last_proof: <int> 前のプルーフ
        :param proof: <int> 現在のプルーフ
        :return: <bool> 正しければ true
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == "0000"


# ------------------------------------------------
# 以下、ローカルマシンにトランザクションエンドポイントを生成する処理
# ------------------------------------------------

# ノード作成
# Flaskの詳細 http://flask.pocoo.org/docs/0.12/quickstart/#a-minimal-application
app = Flask(__name__)

# このノードのグローバルにユニークなアドレスを作る
node_identifier = str(uuid4()).replace('-', '')

# ブロックチェーンクラスをインスタンス化する
blockchain = Blockchain()

# メソッドはPOSTで/transactions/new エンドポイントを作る。POSTなので、データを送信する
@app.route('/transactions/new', methods=['POST'])
def new_transactions():
    values = request.get_json()

    # POSTされたデータのバリデーション
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # 新しいトランザクション作成
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'トランザクションはブロック{index}に追加されました'}

    return jsonify(response), 201

# メソッドはGETで/mineエンドポイントを作る
@app.route('/mine', methods=['GET'])
def mine():
    # 次のプルーフを見つけるためPoWアルゴリズムを使用する
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # プルーフ発見の報酬を得る
    # 送信者は、採掘者が新しいコインを採掘したことを表すために"0"とする
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # チェーンに新しいブロックを加えることで、新しいブロックを採掘
    block = blockchain.new_block(proof)

    response = {
        'message': '新しいブロックを採掘しました',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

# メソッドはGETで、フルのブロックチェーンをリターンする/chainエンドポイントを作る
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

# port5000でサーバーを起動する
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000)
