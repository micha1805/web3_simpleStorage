from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)

install_solc("0.6.0")

# Compile solidity code :
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)
# print(compiled_sol)
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# print(bytecode)

# get ABI
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# print(abi)

# for connecting to rinkeby
w3 = Web3(Web3.HTTPProvider(os.getenv("HTTP_PROVIDER")))
chain_id = 4
my_address = os.getenv("ACCOUNT_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")

# create the contract in python

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# print(SimpleStorage)


# Get latest transaction
nonce = w3.eth.getTransactionCount(my_address)
# print(nonce)
# 1. Build the Contract Deploy Transaction
# 2. Sign the transaction
# 3. Send the transaction


transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)
# print(transaction)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# print(private_key)
# print(signed_txn)

# send the signed transaction
print("Deploying the contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")
# print(tx_receipt)


# working with the contract, we need contract address and contract ABI

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)


# Initial value of favorite number
print(simple_storage.functions.retrieve().call())

# call to simulate the transaction :
# print(simple_storage.functions.store(15).call())


# on fait nonce + 1 car on a deja utilise ce nonce plus haut
print("Updating contract...")
store_transaction = simple_storage.functions.store(23).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)

signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)

tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")
print(simple_storage.functions.retrieve().call())
