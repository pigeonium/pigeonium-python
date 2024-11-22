# pigeonium-python

「ゲームとか独自のコミュニティ用に仮想通貨っぽい雰囲気の通貨を使いたい！」って人に向けた、セットアップが簡単だし作りが雑なやつ

エクスプローラー: https://h4ribote.jp/pigeonium/explorer/transaction/0

## Usage

```python
import pigeonium

newWallet = pigeonium.Wallet.generate()
importedWallet = pigeonium.Wallet.fromPrivate(bytes.fromhex("cdcb58a986c66f7761484633e14a3811c03a1845bae7550f5aa6e41501d4aea7"))

print(pigeonium.API.GET.balance(newWallet.address))

transaction = pigeonium.Transaction.create(importedWallet.privateKey,importedWallet.address,newWallet.address,10000,inputData=b"Hi")

print(pigeonium.API.POST.transaction(transaction).detail)
```
