# Import dependencies

import subprocess 
import json
from dotenv import load_dotenv
import os

# set and load environment variable
load_dotenv
mnemonic = os.getenv('MNEMONIC')


# Import Bit and Web3 dependencies, import from constant.py
from bit import *
from web3 import Web3
from eth_account import Account 
from constants import *
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1.8545"))

# Create derive_wallet function
def derive_wallets(mnemonic, coin, numderive):
    command = 'php hd-wallet-derive.php -g --mnemonic="'+str(mnemonic)+'" --numderive='+str(numderive)+' --coin='+str(coin)+' --format=jsonpretty' 
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    return json.loads(output) 

# Create coins dictionary that store outputs from derive_wallets

coins = {'eth':derive_wallets(mnemonic=mnemonic,coin=ETH,numderive=3),'btc-test': derive_wallets(mnemonic=mnemonic,coin=BTCTEST,numderive=3)}

eth_privatekey = coins['eth'][0]['privkey']
btc_privatekey = coins['btc-test'][0]['privkey']

# Create priv_key_to_account function 

def priv_key_to_account(coin, priv_key):
    
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    
eth_account = priv_key_to_account(ETH,eth_privatekey)
btc_account = priv_key_to_account(BTCTEST,btc_privatekey)

# Create create_tx function 
def create_tx(coin, account, recipient, amount):
    
    global tx_data
    if coin ==ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value": amount}
        )
        tx_data = {
            "to": recipient,
            "from": account.address,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address)
        }
        return tx_data

    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])   
    
# Create send_tx function 

def send_tx(coin, account, recipient, amount):
    
    if coin =='ETH':
        tx_eth = create_tx(coin,account, recipient, amount)
        sign_tx_eth = account.sign_transaction(tx_eth)
        result = w3.eth.sendRawTransaction(sign_tx_eth.rawTransaction)
        print(result.hex())
        return result.hex()
    else:
        tx_btctest= create_tx(coin,account,recipient,amount)
        sign_tx_btctest = account.sign_transaction(tx_btctest)
        from bit.network import NetworkAPI
        NetworkAPI.broadcast_tx_testnet(sign_tx_btctest)       
        return sign_tx_btctest