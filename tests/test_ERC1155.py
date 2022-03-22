from lib2to3.pgen2 import token
import pytest
import brownie

SOMEONE_TOKEN_IDS = [1, 2, 3]
OPERATOR_TOKEN_ID = 10
NEW_TOKEN_ID = 20
INVALID_TOKEN_ID = 99
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ERC165_INTERFACE_ID = (
    "0x0000000000000000000000000000000000000000000000000000000001ffc9a7"
)
ERC1155_INTERFACE_ID = (
    "0x00000000000000000000000000000000000000000000000000000000d9b67a26"
)
INVALID_INTERFACE_ID = (
    "0x0000000000000000000000000000000000000000000000000000000012345678"
)


MAX_UINT256 = (2 ** 256) - 1  # Max uint256 value
TOKEN_NAME = "Ampleia Coin"
TOKEN_SYMBOL = "A14"
TOKEN_DECIMALS = 8
TOKEN_INITIAL_SUPPLY = 1000
TOKEN_SUPPLY_INITIALIZE = 100000000000

GAS_PRICE = 66
GWEI_MULTIPLIER = 10000000000
GAS_PRICE_GWEI = GAS_PRICE * GWEI_MULTIPLIER

TOKEN_NAME_ERC721 = "Lootbox"
TOKEN_SYMBOL_ERC721 = "LOOTBOX"
BASE_URI = "https://opensea-creatures-api.herokuapp.com/api/creature/"

@pytest.fixture
def token_contract_ERC1155(ERC1155, accounts):
    brownie.network.gas_price(GAS_PRICE_GWEI)
    brownie.network.gas_limit(3000000)
    # deploy the contract with the initial value as a constructor argument
    return accounts[0].deploy(ERC1155)


@pytest.fixture
def token_contract_ERC721(ERC721, token_contract_ERC1155, accounts):
    brownie.network.gas_price(GAS_PRICE_GWEI)
    brownie.network.gas_limit(3000000)

    # deploy the contract with the initial value as a constructor argument
    return accounts[0].deploy(
        ERC721,
        TOKEN_NAME_ERC721,
        TOKEN_SYMBOL_ERC721,
        BASE_URI,
        token_contract_ERC1155
    )


@pytest.fixture
def token_contract_ERC20(ERC20, token_contract_ERC1155, accounts):
    brownie.network.gas_price(GAS_PRICE_GWEI)
    brownie.network.gas_limit(3000000)

    # deploy the contract with the initial value as a constructor argument
    return accounts[0].deploy(
        ERC20,
        TOKEN_NAME,
        TOKEN_SYMBOL,
        TOKEN_DECIMALS,
        TOKEN_INITIAL_SUPPLY,
        token_contract_ERC1155,
    )


@pytest.fixture
def contract_link(token_contract_ERC1155, token_contract_ERC20, token_contract_ERC721):
    token_contract_ERC1155.add_contract(token_contract_ERC721)
    token_contract_ERC1155.add_contract(token_contract_ERC20)


def test_run(token_contract_ERC1155):
    assert token_contract_ERC1155.supportsInterface(ERC165_INTERFACE_ID) == 1
    assert token_contract_ERC1155.supportsInterface(ERC1155_INTERFACE_ID) == 1
    assert token_contract_ERC1155.supportsInterface(INVALID_INTERFACE_ID) == 0


def test_mintNft(token_contract_ERC1155, token_contract_ERC721, accounts):
    assert token_contract_ERC1155.addERC721Contract(
        token_contract_ERC721, {"from": accounts[0]})
    txn = token_contract_ERC1155.mintNFT(1, accounts[0], {"from": accounts[0]})
    assert txn.events[1]['_operator'] == accounts[0]
    assert txn.events[1]['_to'] == accounts[0]
    assert txn.events[1]['_value'] == 1
    assert txn.events[1]['_id'] == 1
    assert token_contract_ERC1155.balanceOf(accounts[0], 1) == 1
    token_contract_ERC1155.mintNFT(1, accounts[0], {"from": accounts[0]})
    assert token_contract_ERC1155.uri(1, 1) == "https://opensea-creatures-api.herokuapp.com/api/creature/1"
    assert token_contract_ERC1155.uri(1, 2) == "https://opensea-creatures-api.herokuapp.com/api/creature/2"

# TODO
# # other user try to mint
# def test_mintNftReverts(token_contract_ERC1155, token_contract_ERC721, accounts):
#     assert token_contract_ERC1155.addERC721Contract(
#         token_contract_ERC721, {"from": accounts[0]})
#     with brownie.reverts():
#         token_contract_ERC1155.mintNFT(
#             1, accounts[0], {"from": accounts[1], "allow_revert": True})


def test_mintTokens(token_contract_ERC1155, token_contract_ERC20, accounts):
    assert token_contract_ERC1155.addERC20Contract(
        token_contract_ERC20, {"from": accounts[0]})
    assert token_contract_ERC1155.mintToken(
        1, accounts[1], 100, {"from": accounts[0]})
    assert token_contract_ERC1155.balanceOf(accounts[1], 1) == 100

# TODO
# # other user try to mint
# def test_mintTokensReverts(token_contract_ERC1155, token_contract_ERC20, accounts):
#     assert token_contract_ERC1155.addERC20Contract(
#         token_contract_ERC20, {"from": accounts[0]})
#     with brownie.reverts():
#         # transaction must revert for test to pass
#         token_contract_ERC1155.mintToken(
#             1, accounts[1], 100, {"from": accounts[1], "allow_revert": True})


def test_safeTransferFrom(token_contract_ERC1155, token_contract_ERC20, accounts):
    assert token_contract_ERC1155.addERC20Contract(
        token_contract_ERC20, {"from": accounts[0]})
    assert token_contract_ERC1155.mintToken(
        1, accounts[1], 100, {"from": accounts[0]})
    assert token_contract_ERC1155.balanceOf(accounts[1], 1) == 100
    assert token_contract_ERC1155.setApproveAmount(
        accounts[3], 1, 100,  {"from": accounts[1]})
    assert token_contract_ERC1155.safeTransferFrom(
        accounts[1], accounts[2], 1, 50, "0x00",  {"from": accounts[3]})
    assert token_contract_ERC1155.balanceOf(accounts[1], 1) == 50
    assert token_contract_ERC1155.balanceOf(accounts[2], 1) == 50


# transfer to ZERO_ADDRESS
# contractId doesn't exist
# not enough balance
def test_safeTransferFromReverts(token_contract_ERC1155, token_contract_ERC20, accounts):
    assert token_contract_ERC1155.addERC20Contract(
        token_contract_ERC20, {"from": accounts[0]})
    assert token_contract_ERC1155.mintToken(
        1, accounts[1], 100, {"from": accounts[0]})
    assert token_contract_ERC1155.balanceOf(accounts[1], 1) == 100
    assert token_contract_ERC1155.setApproveAmount(
        accounts[3], 1, 100,  {"from": accounts[1]})
    # with brownie.reverts():
    #     assert token_contract_ERC1155.safeTransferFrom(
    #         accounts[1], accounts[2], 2, 50, "0x00",  {"from": accounts[3]})
    # with brownie.reverts("_to is empty"):
    #     assert token_contract_ERC1155.safeTransferFrom(
    #         accounts[1], ZERO_ADDRESS, 1, 50, "0x00",  {"from": accounts[3]})
    # with brownie.reverts("_from balance is less than _value"):
    #     assert token_contract_ERC1155.safeTransferFrom(
    #         accounts[1], accounts[2], 1, 200, "0x00",  {"from": accounts[3]})


def test_balanceOf(token_contract_ERC1155, token_contract_ERC20, token_contract_ERC721, accounts):
    assert token_contract_ERC1155.addERC20Contract(
        token_contract_ERC20, {"from": accounts[0]})
    assert token_contract_ERC1155.addERC721Contract(
        token_contract_ERC721, {"from": accounts[0]})
    assert token_contract_ERC1155.mintToken(
        1, accounts[1], 100, {"from": accounts[0]})
    assert token_contract_ERC1155.mintNFT(
        2, accounts[1], {"from": accounts[0]})
    assert token_contract_ERC1155.balanceOf(accounts[1], 1) == 100
    assert token_contract_ERC1155.balanceOf(accounts[1], 2) == 1


# tokenId exceeds limit
def test_balanceOfReverts(token_contract_ERC1155, token_contract_ERC20, token_contract_ERC721, accounts):
    assert token_contract_ERC1155.addERC20Contract(
        token_contract_ERC20, {"from": accounts[0]})
    assert token_contract_ERC1155.addERC721Contract(
        token_contract_ERC721, {"from": accounts[0]})
    # with brownie.reverts():
    #     assert token_contract_ERC1155.balanceOf(accounts[1], 3)


def test_AddContract_event(token_contract_ERC1155, token_contract_ERC20, token_contract_ERC721, accounts):
    txn = token_contract_ERC1155.addERC20Contract(
        token_contract_ERC20, {"from": accounts[0]})
    txn2 = token_contract_ERC1155.addERC721Contract(
        token_contract_ERC721, {"from": accounts[0]})

    assert len(txn.events) == 1
    assert len(txn2.events) == 1
    assert txn.events[0]['_contractId'] == 1
    assert txn2.events[0]['_contractId'] == 2


def test_setApproveAmount_event(token_contract_ERC1155, token_contract_ERC20, accounts):
    assert token_contract_ERC1155.addERC20Contract(
        token_contract_ERC20, {"from": accounts[0]})
    assert token_contract_ERC1155.mintToken(
        1, accounts[0], 100, {"from": accounts[0]})
    txn = token_contract_ERC1155.setApproveAmount(
        accounts[1], 1, 50, {"from": accounts[0]})
    assert txn.events[1]["_owner"] == accounts[0]
    assert txn.events[1]["_operator"] == accounts[1]
    assert txn.events[1]["_approved"] == True


def test_setBaseURI(token_contract_ERC1155, token_contract_ERC721, accounts):
    assert token_contract_ERC1155.addERC721Contract(token_contract_ERC721, {"from": accounts[0]})
    assert token_contract_ERC1155.mintNFT(1, accounts[0], {"from": accounts[0]})
    assert token_contract_ERC1155.setBaseURI(1, "test.com/", {"from": accounts[0]})
    assert token_contract_ERC1155.uri(1, 1, {"from": accounts[0]}) == "test.com/1"


def test_name(token_contract_ERC1155, token_contract_ERC721, token_contract_ERC20, accounts):
    assert token_contract_ERC1155.addERC721Contract(token_contract_ERC721, {"from": accounts[0]})
    assert token_contract_ERC1155.addERC20Contract(token_contract_ERC20, {"from": accounts[0]})
    assert token_contract_ERC1155.name(1) == "Lootbox"
    assert token_contract_ERC1155.name(2) == "Ampleia Coin"


def test_symbol(token_contract_ERC1155, token_contract_ERC721, token_contract_ERC20, accounts):
    assert token_contract_ERC1155.addERC721Contract(token_contract_ERC721, {"from": accounts[0]})
    assert token_contract_ERC1155.addERC20Contract(token_contract_ERC20, {"from": accounts[0]})
    assert token_contract_ERC1155.symbol(1) == "LOOTBOX"
    assert token_contract_ERC1155.symbol(2) == "A14"


def test_totalSupply(token_contract_ERC1155, token_contract_ERC721, token_contract_ERC20, accounts):
    # add contracts
    assert token_contract_ERC1155.addERC20Contract(token_contract_ERC20, {"from": accounts[0]})
    assert token_contract_ERC1155.addERC721Contract(token_contract_ERC721, {"from": accounts[0]})

    # check totalSupply of ERC20
    assert token_contract_ERC1155.totalSupply(1) == 1000 * 10 ** TOKEN_DECIMALS

    # check totalSupply of ERC721
    assert token_contract_ERC1155.totalSupply(2) == 0

    # mint tokens
    assert token_contract_ERC1155.mintToken(1, accounts[1], 100, {"from": accounts[0]})
    assert token_contract_ERC1155.balanceOf(accounts[1], 1) == 100

    # mint nfts
    assert token_contract_ERC1155.mintNFT(2, accounts[1], {"from": accounts[0]})
    assert token_contract_ERC1155.balanceOf(accounts[1], 2) == 1

    # check totalSupply of ERC20
    assert token_contract_ERC1155.totalSupply(1) == (1000 * 10 ** TOKEN_DECIMALS) + 100

    # check totalSupply of ERC721
    assert token_contract_ERC1155.totalSupply(2) == 1


def test_destruct(token_contract_ERC1155, accounts):
    token_contract_ERC1155.self_destruct({"from": accounts[0]})
    with pytest.raises(ValueError):
        token_contract_ERC1155.contractCount()
