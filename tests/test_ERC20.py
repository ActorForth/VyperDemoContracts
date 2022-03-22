import pytest
import brownie


MAX_UINT256 = (2 ** 256) - 1  # Max uint256 value
TOKEN_NAME = "Ampleia Coin"
TOKEN_SYMBOL = "A14"
TOKEN_DECIMALS = 8
TOKEN_INITIAL_SUPPLY = 1000
TOKEN_SUPPLY_INITIALIZE = 100000000000


@pytest.fixture
def token_contract(ERC20, accounts):
    # deploy the contract with the initial value as a constructor argument
    return accounts[0].deploy(
        ERC20,
        TOKEN_NAME,
        TOKEN_SYMBOL,
        TOKEN_DECIMALS,
        TOKEN_INITIAL_SUPPLY,
        accounts[0],
    )


def test_simple_transfer(token_contract, accounts):
    token_contract.transfer(accounts[1], 100, {"from": accounts[0]})
    #  remain
    assert token_contract.balanceOf(accounts[0]) == 99999999900
    assert token_contract.balanceOf(accounts[1]) == 100


def test_destruct(token_contract, accounts):
    token_contract.self_destruct({"from": accounts[0]})
    with pytest.raises(ValueError):
        token_contract.balanceOf(accounts[0])


def test_transfer(token_contract, accounts):
    a1, a2, a3 = accounts[1:4]
    # Check total supply, name, symbol and decimals are correctly set
    assert token_contract.totalSupply() == TOKEN_SUPPLY_INITIALIZE
    assert token_contract.name() == TOKEN_NAME
    assert token_contract.symbol() == TOKEN_SYMBOL
    assert token_contract.decimals() == TOKEN_DECIMALS
    # Check several account balances as 0
    assert token_contract.balanceOf(a1) == 0
    assert token_contract.balanceOf(a2) == 0
    assert token_contract.balanceOf(a3) == 0
    # Check several allowances as 0
    assert token_contract.allowance(a1, a1) == 0
    assert token_contract.allowance(a1, a2) == 0
    assert token_contract.allowance(a1, a3) == 0
    assert token_contract.allowance(a2, a3) == 0


def test_mint_and_burn(token_contract, accounts):
    minter, a1, a2 = accounts[0:3]

    # Test scenario were mints 2 to a1, burns twice (check balance consistency)
    assert token_contract.balanceOf(a1) == 0
    token_contract.mint(a1, 2, {"from": minter})
    assert token_contract.balanceOf(a1) == 2
    token_contract.burn(2, {"from": a1})
    assert token_contract.balanceOf(a1) == 0
    # assert_tx_failed(lambda: token_contract.burn(2, {"from": a1}))
    assert token_contract.balanceOf(a1) == 0
    # Test scenario were mintes 0 to a2, burns (check balance consistency, false burn)
    token_contract.mint(a2, 0, {"from": minter})
    assert token_contract.balanceOf(a2) == 0
    # assert_tx_failed(lambda: token_contract.burn(2, {"from": a2}))
    # # Check that a1 cannot burn after depleting their balance
    # assert_tx_failed(lambda: token_contract.burn(1, {"from": a1}))
    # # Check that a1, a2 cannot mint
    # assert_tx_failed(lambda: token_contract.mint(a1, 1, {"from": a1}))
    # assert_tx_failed(lambda: token_contract.mint(a2, 1, {"from": a2}))
    # # Check that mint to ZERO_ADDRESS failed
    # assert_tx_failed(lambda: token_contract.mint(ZERO_ADDRESS, 1, {"from": a1}))
    # assert_tx_failed(lambda: token_contract.mint(ZERO_ADDRESS, 1, {"from": minter}))


def test_totalSupply(token_contract, accounts):
    # Test total supply initially, after mint, between two burns, and after failed burn
    minter, a1 = accounts[0:2]
    assert token_contract.totalSupply() == 100000000000
    token_contract.mint(a1, 2, {"from": minter})
    assert token_contract.totalSupply() == 100000000002
    token_contract.burn(1, {"from": a1})
    assert token_contract.totalSupply() == 100000000001
    token_contract.burn(1, {"from": a1})
    assert token_contract.totalSupply() == 100000000000
    # assert_tx_failed(lambda: token_contract.burn(1, {"from": a1}))
    assert token_contract.totalSupply() == 100000000000
    # Test that 0-valued mint can't affect supply
    token_contract.mint(a1, 0, {"from": minter})
    assert token_contract.totalSupply() == 100000000000


def test_transfer(token_contract, accounts):
    minter, a1, a2 = accounts[0:3]
    # assert_tx_failed(lambda: token_contract.burn(1, {"from": a2}))
    token_contract.mint(a1, 2, {"from": minter})
    token_contract.burn(1, {"from": a1})
    token_contract.transfer(a2, 1, {"from": a1})
    # assert_tx_failed(lambda: token_contract.burn(1, {"from": a1}))
    token_contract.burn(1, {"from": a2})
    # assert_tx_failed(lambda: token_contract.burn(1, {"from": a2}))
    # Ensure transfer fails with insufficient balance
    # assert_tx_failed(lambda: token_contract.transfer(a1, 1, {"from": a2}))
    # Ensure 0-transfer always succeeds
    token_contract.transfer(a1, 0, {"from": a2})


#  TODO
# def test_maxInts(token_contract, accounts):
#     minter, a1, a2 = accounts[0:3]
#     token_contract.mint(a1, MAX_UINT256, {"from": minter})
#     assert token_contract.balanceOf(a1) == MAX_UINT256
#     # assert_tx_failed(lambda: token_contract.mint(a1, 1, {"from": a1}))
#     # assert_tx_failed(lambda: token_contract.mint(a1, MAX_UINT256, {"from": a1}))
#     # Check that totalSupply cannot overflow, even when mint to other account
#     # assert_tx_failed(lambda: token_contract.mint(a2, 1, {"from": minter}))
#     # Check that corresponding mint is allowed after burn
#     token_contract.burn(1, {"from": a1})
#     token_contract.mint(a2, 1, {"from": minter})
#     # assert_tx_failed(lambda: token_contract.mint(a2, 1, {"from": minter}))
#     token_contract.transfer(a1, 1, {"from": a2})
#     # Assert that after obtaining max number of tokens, a1 can transfer those but no more
#     assert token_contract.balanceOf(a1) == MAX_UINT256
#     token_contract.transfer(a2, MAX_UINT256, {"from": a1})
#     assert token_contract.balanceOf(a2) == MAX_UINT256
#     assert token_contract.balanceOf(a1) == 0
#     # [ next line should never work in EVM ]
#     with pytest.raises(ValidationError):
#         token_contract.transfer(a1, MAX_UINT256 + 1, {"from": a2})
#     # Check approve/allowance w max possible token values
#     assert token_contract.balanceOf(a2) == MAX_UINT256
#     token_contract.approve(a1, MAX_UINT256, {"from": a2})
#     token_contract.transferFrom(a2, a1, MAX_UINT256, {"from": a1})
#     assert token_contract.balanceOf(a1) == MAX_UINT256
#     assert token_contract.balanceOf(a2) == 0
#     # Check that max amount can be burned
#     token_contract.burn(MAX_UINT256, {"from": a1})
#     assert token_contract.balanceOf(a1) == 0


def test_transferFrom_and_Allowance(token_contract, accounts):
    minter, a1, a2, a3 = accounts[0:4]
    # assert_tx_failed(lambda: token_contract.burn(1, {"from": a2}))
    token_contract.mint(a1, 1, {"from": minter})
    token_contract.mint(a2, 1, {"from": minter})
    token_contract.burn(1, {"from": a1})
    # This should fail; no allowance or balance (0 always succeeds)
    # assert_tx_failed(lambda: token_contract.transferFrom(a1, a3, 1, {"from": a2}))
    token_contract.transferFrom(a1, a3, 0, {"from": a2})
    # Correct call to approval should update allowance (but not for reverse pair)
    token_contract.approve(a2, 1, {"from": a1})
    assert token_contract.allowance(a1, a2) == 1
    assert token_contract.allowance(a2, a1) == 0
    # transferFrom should succeed when allowed, fail with wrong sender
    # assert_tx_failed(lambda: token_contract.transferFrom(a1, a3, 1, {"from": a3}))
    assert token_contract.balanceOf(a2) == 1
    token_contract.approve(a1, 1, {"from": a2})
    token_contract.transferFrom(a2, a3, 1, {"from": a1})
    # Allowance should be correctly updated after transferFrom
    assert token_contract.allowance(a2, a1) == 0
    # transferFrom with no funds should fail despite approval
    token_contract.approve(a1, 1, {"from": a2})
    assert token_contract.allowance(a2, a1) == 1
    # assert_tx_failed(lambda: token_contract.transferFrom(a2, a3, 1, {"from": a1}))
    # 0-approve should not change balance or allow transferFrom to change balance
    token_contract.mint(a2, 1, {"from": minter})
    assert token_contract.allowance(a2, a1) == 1
    token_contract.approve(a1, 0, {"from": a2})
    assert token_contract.allowance(a2, a1) == 0
    token_contract.approve(a1, 0, {"from": a2})
    assert token_contract.allowance(a2, a1) == 0
    # assert_tx_failed(lambda: token_contract.transferFrom(a2, a3, 1, {"from": a1}))
    # Test that if non-zero approval exists, 0-approval is NOT required to proceed
    # a non-conformant implementation is described in countermeasures at
    # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
    # the final spec insists on NOT using this behavior
    assert token_contract.allowance(a2, a1) == 0
    token_contract.approve(a1, 1, {"from": a2})
    assert token_contract.allowance(a2, a1) == 1
    token_contract.approve(a1, 2, {"from": a2})
    assert token_contract.allowance(a2, a1) == 2
    # Check that approving 0 then amount also works
    token_contract.approve(a1, 0, {"from": a2})
    assert token_contract.allowance(a2, a1) == 0
    token_contract.approve(a1, 5, {"from": a2})
    assert token_contract.allowance(a2, a1) == 5


def test_burnFrom_and_Allowance(token_contract, accounts):
    minter, a1, a2, a3 = accounts[0:4]
    # assert_tx_failed(lambda: token_contract.burn(1, transact={"from": a2}))
    token_contract.mint(a1, 1, {"from": minter})
    token_contract.mint(a2, 1, {"from": minter})
    token_contract.burn(1, {"from": a1})
    # This should fail; no allowance or balance (0 always succeeds)
    # assert_tx_failed(lambda: token_contract.burnFrom(a1, 1,  {"from": a2}))
    token_contract.burnFrom(a1, 0, {"from": a2})
    # Correct call to approval should update allowance (but not for reverse pair)
    token_contract.approve(a2, 1, {"from": a1})
    assert token_contract.allowance(a1, a2) == 1
    assert token_contract.allowance(a2, a1) == 0
    # transferFrom should succeed when allowed, fail with wrong sender
    # assert_tx_failed(lambda: token_contract.burnFrom(a2, 1,  {"from": a3}))
    assert token_contract.balanceOf(a2) == 1
    token_contract.approve(a1, 1, {"from": a2})
    token_contract.burnFrom(a2, 1, {"from": a1})
    # Allowance should be correctly updated after transferFrom
    assert token_contract.allowance(a2, a1) == 0
    # transferFrom with no funds should fail despite approval
    token_contract.approve(a1, 1, {"from": a2})
    assert token_contract.allowance(a2, a1) == 1
    # assert_tx_failed(lambda: token_contract.burnFrom(a2, 1,  {"from": a1}))
    # 0-approve should not change balance or allow transferFrom to change balance
    token_contract.mint(a2, 1, {"from": minter})
    assert token_contract.allowance(a2, a1) == 1
    token_contract.approve(a1, 0, {"from": a2})
    assert token_contract.allowance(a2, a1) == 0
    token_contract.approve(a1, 0, {"from": a2})
    assert token_contract.allowance(a2, a1) == 0
    # assert_tx_failed(lambda: token_contract.burnFrom(a2, 1,  {"from": a1}))
    # Test that if non-zero approval exists, 0-approval is NOT required to proceed
    # a non-conformant implementation is described in countermeasures at
    # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
    # the final spec insists on NOT using this behavior
    assert token_contract.allowance(a2, a1) == 0
    token_contract.approve(a1, 1, {"from": a2})
    assert token_contract.allowance(a2, a1) == 1
    token_contract.approve(a1, 2, {"from": a2})
    assert token_contract.allowance(a2, a1) == 2
    # Check that approving 0 then amount also works
    token_contract.approve(a1, 0, {"from": a2})
    assert token_contract.allowance(a2, a1) == 0
    token_contract.approve(a1, 5, {"from": a2})
    assert token_contract.allowance(a2, a1) == 5
    # Check that burnFrom to ZERO_ADDRESS failed
    # assert_tx_failed(
    # lambda: token_contract.burnFrom(ZERO_ADDRESS, 0, transact={"from": a1})
    # )
