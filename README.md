# BlockchainDemo
Python3 &amp; Flaskで動く、簡素なブロックチェーン

## 参考サイト：
ブロックチェーンを作ることで学ぶ 〜ブロックチェーンがどのように動いているのか学ぶ最速の方法は作ってみることだ〜
https://qiita.com/hidehiro98/items/841ece65d896aeaa8a2a

## 動作環境:
1. python 3.6以上 & pip
2. pip でFlaskとRequest libraryをインストール

```
pip install Flask==0.12.2 requests==2.18.4
```

3. jsonでリクエストを投げるため、Postmanをインストール

## 実行手順
### 1. サーバーの起動
```bash
$ python blockchain.py
```

### 2. リクエスト
#### 採掘
POSTMAN（cURLでも可）
http://localhost:5000/mine に GETリクエストを送信すると、採掘できます。

#### 採掘したブロックに新しいトランザクションを作る
http://localhost:5000/transactions/new に POSTリクエストを送信する。
```
{
  "sender": <採掘で取得したレスポンスのrecipientのハッシュ値>,
  "recipient": "someone-other-address",
  "amount": 5
}
```

#### 採掘したブロックを取得する
http://localhost:5000/chain に GETリクエストを投げると、採掘済みのブロックをすべて取得できます。

### 3. （WIP）コンセンサス：非中央集権的な、ブロックチェーン確認処理
