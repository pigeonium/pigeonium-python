# pigeonium-python

「ゲームとか独自のコミュニティ用に仮想通貨っぽい雰囲気の通貨を使いたい！」って人に向けた、セットアップが簡単だし作りが雑なやつ

エクスプローラー: https://h4ribote.jp/pigeonium/explorer/transaction.html?indexId=0

## Usage

```python
from pigeonium import *

newWallet = Wallet.generate()
importedWallet = Wallet.fromPrivate(bytes.fromhex("cdcb58a986c66f7761484633e14a3811c03a1845bae7550f5aa6e41501d4aea7"))

print(API.GET.balance(newWallet.address))

transaction = Transaction.create(importedWallet.privateKey,importedWallet.address,newWallet.address,10000,inputData=b"Hi")

print(API.POST.transaction(transaction).detail)
```
