from ecdsa import SigningKey, VerifyingKey, NIST256p
import hashlib
import requests

PIGEONIUM_PRIME = 9223372036854775057
TRANSACTION_FEE = 100000 # per 1byte

def double_hash(data:bytes):
    sha256_hashed = hashlib.sha256(data).digest()
    md5_hashed = hashlib.md5(sha256_hashed).digest()
    return md5_hashed

class base62:
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    def frombytes(byte:bytes):
        num = int(byte.hex(), 16)
        base62_str = ''
        while num > 0:
            remainder = num % 62
            base62_str = base62.chars[remainder] + base62_str
            num = num // 62
        return base62_str

    def fromhex(string:str):
        num = int(string, 16)
        base62_str = ''
        while num > 0:
            remainder = num % 62
            base62_str = base62.chars[remainder] + base62_str
            num = num // 62
        return base62_str

    def fromint(integer:int):
        base62_str = ''
        while integer > 0:
            remainder = integer % 62
            base62_str = base62.chars[remainder] + base62_str
            integer = integer // 62
        return base62_str

class Wallet:
    def __init__(self) -> None:
        self.privateKey:bytes = None
        self.publicKey:bytes = None
        self.address:str = None
    
    def __str__(self) -> str:
        return self.address
    
    @classmethod
    def generate(cls):
        wallet = cls()
        private_key = SigningKey.generate(NIST256p)
        public_key = private_key.get_verifying_key().to_string()
        public_hash = double_hash(public_key)
        wallet.privateKey = private_key.to_string()
        wallet.publicKey = public_key
        wallet.address = base62.frombytes(public_hash)

        return wallet
        
    @classmethod
    def fromPrivate(cls,privateKey:bytes):
        wallet = cls()
        private_key = SigningKey.from_string(privateKey,NIST256p)
        public_key = private_key.get_verifying_key().to_string()
        wallet.privateKey = private_key.to_string()
        wallet.publicKey = public_key
        public_hash = double_hash(public_key)
        wallet.address = base62.frombytes(public_hash)
        return wallet
    
    @classmethod
    def fromPublic(cls,publicKey:bytes):
        wallet = cls()
        wallet.privateKey = None
        wallet.publicKey = publicKey
        public_hash = double_hash(publicKey)
        wallet.address = base62.frombytes(public_hash)
        return wallet
    
    def sign(self,data:bytes):
        private_key = SigningKey.from_string(self.privateKey,NIST256p)
        signature = bytes.fromhex(private_key.sign(data).hex())
        return signature

    def verify_signature(self,signature:bytes,data:bytes):
        public_key = VerifyingKey.from_string(bytes.fromhex(self.publicKey),NIST256p)
        try:
            if public_key.verify(signature,data):
                return True
            else:
                return False
        except:
            return False
    
    def showInfo(self):
        print(f"privateKey | {self.privateKey.hex()}")
        print(f"publicKey  | {self.publicKey.hex()}")
        print(f"address    | {self.address}")

class Token:
    def __init__(self) -> None:
        self.tokenId:int = None
        self.name:str = None
        self.symbol:str = None
        self.issuer:str = None
    
    @classmethod
    def create(cls,name:str,symbol:str,issuer:str):
        token = cls()
        tokenId = int(hashlib.sha256(f"{name}{symbol}{issuer}".encode()).hexdigest(),16)%PIGEONIUM_PRIME
        token.name = name
        token.symbol = symbol
        token.issuer = issuer
        token.tokenId = tokenId
        return token
    
    def verify(self):
        return self.tokenId == int(hashlib.sha256(f"{self.name}{self.symbol}{self.issuer}".encode()).hexdigest(),16)%PIGEONIUM_PRIME
    
    def showInfo(self):
        print(f"tokenId | {self.tokenId}")
        print(f"name    | {self.name}")
        print(f"symbol  | {self.symbol}")
        print(f"issuer  | {self.issuer}")
    
    def inputData(self,issuanceVolume:int):
        if issuanceVolume > 100000000000000000:
            raise ValueError("The maximum 'issuanceVolume' is 100,000,000,000.000000(10^17)")
        data = f"{self.tokenId},{self.name},{self.symbol},{self.issuer},{issuanceVolume}".encode()
        return data

class Transaction:
    def __init__(self) -> None:
        self.indexId:int = None
        self.transactionId:str = None
        self.source:str = None
        self.dest:str = None
        self.amount:int = None
        self.tokenId:int = None
        self.tokenAmount:int = None
        self.transactionFee:int = None
        self.inputData:bytes = None
        self.publicKey:bytes = None
    
    def showInfo(self):
        print(f"indexId        | {self.indexId}")
        print(f"transactionId  | {self.transactionId}")
        print(f"source         | {self.source}")
        print(f"dest           | {self.dest}")
        print(f"amount         | {self.amount}")
        print(f"tokenId        | {self.tokenId}")
        print(f"tokenAmount    | {self.tokenAmount}")
        print(f"transactionFee | {self.transactionFee}")
        print(f"inputData      | {self.inputData.hex()}")
        print(f"publicKey      | {self.publicKey.hex()}")
        return None
    
    @classmethod
    def create(cls,privateKey:bytes,source:str,dest:str,amount:int,tokenId:int=0,tokenAmount:int=0,inputData:bytes=bytes()):
        transaction = cls()
        transaction_data = hashlib.sha256(f"{source}{dest}{amount}{tokenId}{tokenAmount}"
                                          f"{inputData.hex()}".encode()).digest()
        transaction_id = SigningKey.from_string(privateKey,NIST256p).sign(transaction_data).hex()
        transaction.indexId = None
        transaction.transactionId = transaction_id
        transaction.source = source
        transaction.dest = dest
        transaction.amount = amount
        transaction.tokenId = tokenId
        transaction.tokenAmount = tokenAmount
        if inputData:
            transaction.transactionFee = len(inputData)*TRANSACTION_FEE
        else:
            transaction.transactionFee = None
        transaction.inputData = inputData
        transaction.publicKey = SigningKey.from_string(privateKey,NIST256p).get_verifying_key().to_string()
        
        return transaction
    
    def verify(self):
        transaction_data = hashlib.sha256(f"{self.source}{self.dest}{self.amount}{self.tokenId}{self.tokenAmount}"
                                          f"{self.inputData.hex()}".encode()).digest()
        public_key = VerifyingKey.from_string(self.publicKey,NIST256p)
        try:
            if public_key.verify(bytes.fromhex(self.transactionId),transaction_data):
                return True
            else:
                return False
        except:
            return False


class API:
    VERSION = 1
    SERVER = f"https://pigeonium.h4ribote.net/api/v{VERSION}"

    class RESPONSE:
        def __init__(self,code:int,message:str,detail:str,info:dict={}) -> None:
            self.code:int = code
            self.message:str = message
            self.detail:str = detail
            self.info:dict = info
        
        def __str__(self) -> str:
            dct = {'code':self.code,'message':self.message,'detail':self.detail}
            return f"{dct}"
        
        def error(self):
            if self.code >= 400:
                return True
            else:
                return False
        
        def raiseErr(self):
            if self.code >= 400:
                raise Exception()

    @staticmethod
    def post(uri:str,data = {}):
        url = API.SERVER + uri
        response = requests.post(url, data).json()
        return API.RESPONSE(int(response['code']),response['message'],response['detail'],{'indexId':int(response.get('indexId',-1))})
    
    @staticmethod
    def get(uri:str,params = {}):
        url = API.SERVER + uri
        response = requests.get(url,params)
        return response.json()
    
    class POST:
        @staticmethod
        def transaction(transaction:Transaction):
            data = {
                'transactionId': transaction.transactionId,
                'source': transaction.source,
                'dest': transaction.dest,
                'amount': transaction.amount,
                'tokenId': transaction.tokenId,
                'tokenAmount': transaction.tokenAmount,
                'inputData': transaction.inputData.hex(),
                'publicKey': transaction.publicKey.hex()
            }
            return API.post('/post/transaction',data)
        

    class GET:
        @staticmethod
        def transaction(transactionId:str = None,indexId:int = None,address:str = None,source:str = None,dest:str = None,tokenId:int = None,indexId_from:int = None):
            """return [[Transaction,timestamp]]"""
            params = {
                'transactionId':transactionId,
                'indexId':indexId,
                'address':address,
                'source':source,
                'dest':dest,
                'tokenId':tokenId,
                'indexId_from':indexId_from
            }
            response = API.get('/explorer/transaction',params)
            transactions = []
            for i in response:
                transaction = Transaction()
                transaction.indexId = int(i['indexId'])
                transaction.transactionId = i['transactionId']
                transaction.source = i['source']
                transaction.dest = i['dest']
                transaction.amount = int(i['amount'])
                transaction.tokenId = int(i['tokenId'])
                transaction.tokenAmount = int(i['tokenAmount'])
                transaction.transactionFee = int(i['transactionFee'])
                transaction.inputData = bytes.fromhex(i['inputData'])
                transaction.publicKey = bytes.fromhex(i['publicKey'])
                timestamp = int(i['timestamp'])
                transactions.append([transaction,timestamp])
            return transactions
        
        @staticmethod
        def balance(address:str = None):
            params = {'address':address}
            return API.get('/explorer/balance',params)
    
        @staticmethod
        def token_balance(address:str = None,tokenId:int = None):
            params = {'address':address,'tokenId':tokenId}
            return API.get('/explorer/token_balance',params)
        
        @staticmethod
        def tokens(issuer:str = None, tokenId:int = None):
            params = {'issuer':issuer,'tokenId':tokenId}
            response = API.get('/explorer/tokens',params)
            tokenlist:list[Token] = []
            for tokeninfo in response:
                token = Token()
                token.tokenId = int(tokeninfo['tokenId'])
                token.name = tokeninfo['name']
                token.symbol = tokeninfo['symbol']
                token.issuer = tokeninfo['issuer']
                tokenlist.append(token)
            return tokenlist
        
