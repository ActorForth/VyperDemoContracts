from brownie import ERC20, ERC721, accounts
import os

TOKEN_NAME = " Ampleia Coin"
TOKEN_SYMBOL = "A14"
TOKEN_DECIMALS = 8
TOKEN_INITIAL_SUPPLY = 1000
TOKEN_SUPPLY_INITIALIZE = 100000000000
GWEI_MULTIPLIER = 10000000000
GAS_PRICE = 166 * GWEI_MULTIPLIER

PRIVATE_KEY = os.getenv('PRIVATE_KEY')

def main():
    accounts.add(PRIVATE_KEY)
    # ERC20.deploy(
    #     TOKEN_NAME,
    #     TOKEN_SYMBOL,
    #     TOKEN_DECIMALS,
    #     TOKEN_INITIAL_SUPPLY,
    #     accounts[0],
    #     {"from": accounts[0],"gas_price": GAS_PRICE}
    # )
    ERC721.deploy(accounts[0], {"from": accounts[0],"gas_price": GAS_PRICE}
)
