import pytest
import brownie

SOMEONE_TOKEN_IDS = [1, 2, 3, 4, 5, 6, 7, 8 ,9, 10]
OPERATOR_TOKEN_ID = 11
NEW_TOKEN_ID = 20
INVALID_TOKEN_ID = 99
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ERC165_INTERFACE_ID = (
    "0x0000000000000000000000000000000000000000000000000000000001ffc9a7"
)
SurpriseBox721_INTERFACE_ID = (
    "0x0000000000000000000000000000000000000000000000000000000080ac58cd"
)
INVALID_INTERFACE_ID = (
    "0x0000000000000000000000000000000000000000000000000000000012345678"
)
GAS_PRICE = 66
GWEI_MULTIPLIER = 10000000000
GAS_PRICE_GWEI = GAS_PRICE * GWEI_MULTIPLIER

TOKEN_NAME = "Lootbox"
TOKEN_SYMBOL = "LOOTBOK"
BASE_URI = "https://opensea-creatures-api.herokuapp.com/api/creature/"


@pytest.fixture
def token_contract(SurpriseBox721, accounts):
    brownie.network.gas_price(GAS_PRICE_GWEI)

    minter, someone, operator = accounts[:3]

    # deploy the contract with the initial value as a constructor argument
    contract = accounts[0].deploy(
        SurpriseBox721,
        TOKEN_NAME,
        TOKEN_SYMBOL,
        BASE_URI,
        #accounts[0]
        minter
    )

    # someone owns 3 tokens
    for i in SOMEONE_TOKEN_IDS:
        contract.mint(someone, {"from": minter})

    contract.mint(operator, {"from": minter})

    return contract


def test_supportsInterface(token_contract):
    assert token_contract.supportsInterface(ERC165_INTERFACE_ID) == 1
    assert token_contract.supportsInterface(SurpriseBox721_INTERFACE_ID) == 1
    assert token_contract.supportsInterface(INVALID_INTERFACE_ID) == 0
    assert token_contract.supportsInterface("1ffc9a7") == 1
    assert token_contract.supportsInterface("0x1ffc9a7") == 1
    assert token_contract.supportsInterface("0x01ffc9a7") == 1

    assert token_contract.supportsInterface("80ac58cd") == 1




def test_balanceOf(token_contract, accounts):
    someone = accounts[1]
    assert token_contract.balanceOf(someone) == len(SOMEONE_TOKEN_IDS)
    # assert_tx_failed(lambda: token_contract.balanceOf(ZERO_ADDRESS))


def test_ownerOf(token_contract, accounts):
    someone = accounts[1]
    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[0]) == someone
    # assert_tx_failed(lambda: token_contract.ownerOf(INVALID_TOKEN_ID))


def test_getApproved(token_contract, accounts):
    someone, operator = accounts[1:3]

    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[1]) == someone

    assert token_contract.getApproved(SOMEONE_TOKEN_IDS[1]) == ZERO_ADDRESS

    token_contract.approve(operator, SOMEONE_TOKEN_IDS[1], {"from": someone})

    assert token_contract.getApproved(SOMEONE_TOKEN_IDS[1]) == operator


def test_isApprovedForAll(token_contract, accounts):
    someone, operator = accounts[1:3]

    assert token_contract.isApprovedForAll(someone, operator) == 0

    token_contract.setApprovalForAll(operator, True, {"from": someone})

    assert token_contract.isApprovedForAll(someone, operator) == 1


def test_transferFrom_by_owner(token_contract, accounts):
    someone, operator = accounts[1:3]

    # transfer from zero address

    # assert_tx = token_contract.transferFrom(
    #     ZERO_ADDRESS, operator, SOMEONE_TOKEN_IDS[0], {"from": someone}
    # )
    #
    # # transfer to zero address
    # assert_tx_failed(
    #     lambda: token_contract.transferFrom(
    #         someone, ZERO_ADDRESS, SOMEONE_TOKEN_IDS[0], {"from": someone}
    #     )
    # )
    #
    # # transfer token without ownership
    # assert_tx_failed(
    #     lambda: token_contract.transferFrom(
    #         someone, operator, OPERATOR_TOKEN_ID, {"from": someone}
    #     )
    # )
    #
    # # transfer invalid token
    # assert_tx_failed(
    #     lambda: token_contract.transferFrom(
    #         someone, operator, INVALID_TOKEN_ID, {"from": someone}
    #     )
    # )

    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[2]) == someone

    # transfer by owner
    tx_hash = token_contract.transferFrom(
        someone, operator, SOMEONE_TOKEN_IDS[2], {"from": someone}
    )

    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[2]) == operator
    assert token_contract.balanceOf(someone) == len(SOMEONE_TOKEN_IDS) - 1
    assert token_contract.balanceOf(operator) == 2


def test_transferFrom_by_approved(token_contract, accounts):
    someone, operator = accounts[1:3]

    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[3]) == someone

    # transfer by approved
    token_contract.approve(operator, SOMEONE_TOKEN_IDS[3], {"from": someone})
    tx_hash = token_contract.transferFrom(
        someone, operator, SOMEONE_TOKEN_IDS[3], {"from": operator}
    )

    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[3]) == operator
    assert token_contract.balanceOf(someone) == len(SOMEONE_TOKEN_IDS) - 1
    assert token_contract.balanceOf(operator) == 2


def test_transferFrom_by_operator(token_contract, accounts):
    someone, operator = accounts[1:3]

    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[4]) == someone

    # transfer by operator
    token_contract.setApprovalForAll(operator, True, {"from": someone})
    tx_hash = token_contract.transferFrom(
        someone, operator, SOMEONE_TOKEN_IDS[4], {"from": operator}
    )

    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[4]) == operator
    assert token_contract.balanceOf(someone) == len(SOMEONE_TOKEN_IDS) - 1
    assert token_contract.balanceOf(operator) == 2


def test_safeTransferFrom_by_owner(token_contract, accounts):
    someone, operator = accounts[1:3]

    # # transfer from zero address
    # assert_tx_failed(
    #     lambda: token_contract.safeTransferFrom(
    #         ZERO_ADDRESS, operator, SOMEONE_TOKEN_IDS[0],  {"from": someone}
    #     )
    # )
    #
    # # transfer to zero address
    # assert_tx_failed(
    #     lambda: token_contract.safeTransferFrom(
    #         someone, ZERO_ADDRESS, SOMEONE_TOKEN_IDS[0],  {"from": someone}
    #     )
    # )
    #
    # # transfer token without ownership
    # assert_tx_failed(
    #     lambda: token_contract.safeTransferFrom(
    #         someone, operator, OPERATOR_TOKEN_ID,  {"from": someone}
    #     )
    # )
    #
    # # transfer invalid token
    # assert_tx_failed(
    #     lambda: token_contract.safeTransferFrom(
    #         someone, operator, INVALID_TOKEN_ID,  {"from": someone}
    #     )
    # )

    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[5]) == someone

    # transfer by owner
    tx_hash = token_contract.safeTransferFrom(
        someone, operator, SOMEONE_TOKEN_IDS[5], {"from": someone}
    )

    # logs = get_logs(tx_hash, token_contract, "Transfer")
    #
    # assert len(logs) > 0
    # args = logs[0].args
    # assert args.sender == someone
    # assert args.receiver == operator
    # assert args.tokenId == SOMEONE_TOKEN_IDS[0]
    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[5]) == operator
    assert token_contract.balanceOf(someone) == len(SOMEONE_TOKEN_IDS) - 1
    assert token_contract.balanceOf(operator) == 2

def test_safeTransferFrom_by_owner(token_contract, accounts):
    someone, operator = accounts[1:3]

    # # transfer from zero address
    # assert_tx_failed(
    #     lambda: token_contract.safeTransferFrom(
    #         ZERO_ADDRESS, operator, SOMEONE_TOKEN_IDS[0],  {"from": someone}
    #     )
    # )
    #
    # # transfer to zero address
    # assert_tx_failed(
    #     lambda: token_contract.safeTransferFrom(
    #         someone, ZERO_ADDRESS, SOMEONE_TOKEN_IDS[0],  {"from": someone}
    #     )
    # )
    #
    # # transfer token without ownership
    # assert_tx_failed(
    #     lambda: token_contract.safeTransferFrom(
    #         someone, operator, OPERATOR_TOKEN_ID,  {"from": someone}
    #     )
    # )
    #
    # # transfer invalid token
    # assert_tx_failed(
    #     lambda: token_contract.safeTransferFrom(
    #         someone, operator, INVALID_TOKEN_ID,  {"from": someone}
    #     )
    # )

    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[6]) == someone

    # transfer by owner
    tx_hash = token_contract.safeTransferFrom(
        someone, operator, SOMEONE_TOKEN_IDS[6], b"101", {"from": someone}
    )

    # logs = get_logs(tx_hash, token_contract, "Transfer")
    #
    # assert len(logs) > 0
    # args = logs[0].args
    # assert args.sender == someone
    # assert args.receiver == operator
    # assert args.tokenId == SOMEONE_TOKEN_IDS[0]
    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[6]) == operator
    assert token_contract.balanceOf(someone) == len(SOMEONE_TOKEN_IDS) - 1
    assert token_contract.balanceOf(operator) == 2

def test_safeTransferFrom_by_approved(token_contract, accounts):
    someone, operator = accounts[1:3]

    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[7]) == someone

    # transfer by approved
    token_contract.approve(operator, SOMEONE_TOKEN_IDS[7], {"from": someone})
    tx_hash = token_contract.safeTransferFrom(
        someone, operator, SOMEONE_TOKEN_IDS[7], {"from": operator}
    )

    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[7]) == operator
    assert token_contract.balanceOf(someone) == len(SOMEONE_TOKEN_IDS) - 1
    assert token_contract.balanceOf(operator) == 2


def test_safeTransferFrom_by_operator(token_contract, accounts):
    someone, operator = accounts[1:3]

    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[7]) == someone

    # transfer by operator
    token_contract.setApprovalForAll(operator, True, {"from": someone})
    tx_hash = token_contract.safeTransferFrom(
        someone, operator, SOMEONE_TOKEN_IDS[7], {"from": operator}
    )

    # logs = get_logs(tx_hash, token_contract, "Transfer")
    #
    # assert len(logs) > 0
    # args = logs[0].args
    # assert args.sender == someone
    # assert args.receiver == operator
    # assert args.tokenId == SOMEONE_TOKEN_IDS[2]
    assert token_contract.ownerOf(SOMEONE_TOKEN_IDS[7]) == operator
    assert token_contract.balanceOf(someone) == len(SOMEONE_TOKEN_IDS) - 1
    assert token_contract.balanceOf(operator) == 2


def test_destruct(token_contract, accounts):
    token_contract.self_destruct({"from": accounts[0]})
    with pytest.raises(ValueError):
        token_contract.balanceOf(accounts[0])
