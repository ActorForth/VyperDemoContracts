# @version 0.3.1

# Interfaces

interface ERC1155Receiver:
    def onERC1155Received(
        _operator: address,
        _from: address,
        _token_id: uint256,
        _value: uint256,
        _data: Bytes[1024]
    ) -> Bytes[4]: payable
    def onERC1155BatchReceived(
        _operator: address,
        _from: address,
        _token_ids: uint256[100],
        _values: uint256[100],
        _data: Bytes[1024]
    ) -> Bytes[4]: payable


interface ERC721:
    def mint(_to: address) -> bool: nonpayable
    def balanceOf(_owner: address) -> uint256: view
    def tokenURI(_tokenId: uint256) -> String[256]: view
    def setBaseURI(_uri: String[256]): nonpayable
    def name() -> String[64]: view
    def symbol() -> String[32]: view
    def totalSupply() -> uint256: view
    def self_destruct(): view


interface ERC20:
    def mint(_to: address, _value: uint256): nonpayable
    def safeTransferFrom(_operator: address, _from: address, _to: address, _value: uint256): nonpayable
    def balanceOf(_owner: address) -> uint256: view
    def setApprove(_owner: address, _spender: address, _value: uint256): nonpayable
    def name() -> String[64]: view
    def symbol() -> String[32]: view
    def totalSupply() -> uint256: view
    def self_destruct(): view

# Events
event TransferSingle:
    _operator: indexed(address)
    _from: indexed(address)
    _to: indexed(address)
    _id: uint256
    _value: uint256


event TransferBatch:
    _operator: indexed(address)
    _from: indexed(address)
    _to: indexed(address[10])
    _ids: uint256[10]
    _values: uint256[10]


event ApprovalForAll:
    _owner: indexed(address)
    _operator: indexed(address)
    _approved: bool


event URI:
    _value: String[100]
    _id: indexed(uint256)


event AddContract:
    _contractAddress: indexed(address)
    _contractId: uint256


# Constants

ERC1155_BATCH_ACCEPTED: constant(Bytes[4]) = b'\xbc\x19\x7c\x81'

ERC1155_ACCEPTED: constant(Bytes[4]) = b'\xf2\x3a\x6e\x61'

BYTE_SIZE: constant(uint256) = 10

MAX_BATCH_SIZE: constant(uint256) = 100

# @dev Mapping of interface id to bool about whether or not it's supported
supportedInterfaces: HashMap[bytes32, bool]

# @dev ERC165 interface ID of ERC165
ERC165_INTERFACE_ID: constant(bytes32) = 0x0000000000000000000000000000000000000000000000000000000001ffc9a7

# @dev ERC165 interface ID of ERC1155
ERC1155_INTERFACE_ID: constant(bytes32) = 0x00000000000000000000000000000000000000000000000000000000d9b67a26


# Values

idToERC20ContractAddress: public(HashMap[uint256, address])
idToERC721ContractAddress: public(HashMap[uint256, address])
minter: public(address)
contractCount: public(uint256)


# Functions

SUPPORTED_INTERFACES: constant(bytes32[2]) = [

    0x01ffc9a700000000000000000000000000000000000000000000000000000000,

    0xd9b67a2600000000000000000000000000000000000000000000000000000000
    
]


@external
def __init__():
    self.minter = msg.sender
    self.supportedInterfaces[ERC165_INTERFACE_ID] = True
    self.supportedInterfaces[ERC1155_INTERFACE_ID] = True
    self.contractCount = 0


@external
def __default__() -> bool:
    method: bytes4 = convert(slice(msg.data, 0, 4), bytes4)
    assert method == 0x01ffc9a7
    interface_id: bytes32 = convert(slice(msg.data, 4, 32), bytes32)
    return interface_id in SUPPORTED_INTERFACES


@internal
def _doSafeTransferAcceptanceCheck(
    _operator: address,
    _from: address,
    _to: address,
    _tokenId: uint256,
    _value: uint256,
    _data: Bytes[BYTE_SIZE]
):
    tempCheckingBytes: Bytes[4] = ERC1155Receiver(_to).onERC1155Received(_operator, _from, _tokenId, _value, _data)
    tempAccepted: Bytes[4] = ERC1155_ACCEPTED

    checkingBytes: Bytes[4] = tempCheckingBytes
    accepted: Bytes[4] = tempAccepted

    assert checkingBytes == accepted


@internal
def _doSafeBatchTransferAcceptanceCheck(
    _operator: address,
    _from: address,
    _to: address,
    _tokenIds: uint256[MAX_BATCH_SIZE],
    _values: uint256[MAX_BATCH_SIZE],
    _data: Bytes[BYTE_SIZE]
):
    tempCheckingBytes: Bytes[4] = ERC1155Receiver(_to).onERC1155BatchReceived(_operator, _from, _tokenIds, _values, _data)
    tempAccepted: Bytes[4] = ERC1155_BATCH_ACCEPTED

    checkingBytes: Bytes[4] = tempCheckingBytes
    accepted: Bytes[4] = tempAccepted

    assert checkingBytes == accepted


@view
@external
def supportsInterface(_interfaceID: bytes32) -> bool:
    """
    @dev Interface identification is specified in ERC-165.
    @param _interfaceID Id of the interface
    """
    return self.supportedInterfaces[_interfaceID]


@external
def safeTransferFrom(_from: address, _to: address, _id: uint256, _value: uint256, _data: Bytes[10]):
    assert _to != ZERO_ADDRESS, "_to is empty"
    contract_address: address = self.idToERC20ContractAddress[_id]
    assert contract_address != ZERO_ADDRESS
    balanceOfSender:uint256 = ERC20(contract_address).balanceOf(_from)
    assert balanceOfSender >= _value, "_from balance is less than _value"
    ERC20(contract_address).safeTransferFrom(msg.sender,_from, _to, _value)
    log TransferSingle (msg.sender, _from, _to, _id, _value)
    if _to.is_contract:
        self._doSafeTransferAcceptanceCheck(msg.sender, _from, _to, _id, _value, _data)


@external
def setApprovalForAll(_operator: address, _approved: bool):
    pass


@view
@external
def isApprovedForAll(_owner: address, _operator: address) -> bool:
    return False


@external
@view
def balanceOfBatch(_owners: address[MAX_BATCH_SIZE], _tokenIds: uint256[MAX_BATCH_SIZE]) -> uint256[3]:
    balances_: uint256[3] = [1,2,3]
    return balances_


@view
@external
def balanceOf(_owner: address, _contractId: uint256) -> uint256:
    assert _contractId <= self.contractCount
    _balanceOf: uint256 = 0 
    if self.idToERC20ContractAddress[_contractId] != ZERO_ADDRESS:
        _balanceOf = ERC20(self.idToERC20ContractAddress[_contractId]).balanceOf(_owner)
    else:
        _balanceOf = ERC721(self.idToERC721ContractAddress[_contractId]).balanceOf(_owner)
    return _balanceOf


@external
def safeBatchTransferFrom(_from: address, _to: address, calldata: uint256[128], _ids: uint256[10], _values: uint256[10], _data: Bytes[256]):
    pass


@external
def mintNFT(_contract_id: uint256, _to: address):
    assert msg.sender == self.minter
    contract_address: address = self.idToERC721ContractAddress[_contract_id]
    assert contract_address != ZERO_ADDRESS
    ERC721(contract_address).mint(_to)
    log TransferSingle(msg.sender, ZERO_ADDRESS, _to, _contract_id, 1)


@external
def mintToken(_contract_id: uint256, _to: address, _value: uint256):
    assert msg.sender == self.minter
    contract_address: address = self.idToERC20ContractAddress[_contract_id]
    assert contract_address != ZERO_ADDRESS
    ERC20(contract_address).mint(_to, _value)
    log TransferSingle(msg.sender, ZERO_ADDRESS, _to, _contract_id, _value)


@external
def addERC20Contract(_address: address):
    assert msg.sender == self.minter
    assert _address != ZERO_ADDRESS
    self.contractCount += 1
    self.idToERC20ContractAddress[self.contractCount] = _address
    log AddContract(_address, self.contractCount)


@external
def addERC721Contract(_address: address):
    assert msg.sender == self.minter
    assert _address != ZERO_ADDRESS
    self.contractCount += 1
    self.idToERC721ContractAddress[self.contractCount] = _address
    log AddContract(_address, self.contractCount)


@external 
def setApproveAmount(_operator: address, _contract_id: uint256, _value: uint256):
    assert _operator != ZERO_ADDRESS
    contract_address: address = self.idToERC20ContractAddress[_contract_id]
    assert contract_address != ZERO_ADDRESS
    ERC20(contract_address).setApprove(msg.sender, _operator, _value)
    log ApprovalForAll(msg.sender, _operator, True)


@view
@external
def uri(_contractId: uint256, _tokenId: uint256) -> String[256]:
    assert _contractId <= self.contractCount
    assert self.idToERC721ContractAddress[_contractId] != ZERO_ADDRESS
    _uri: String[256] = ""
    _uri = ERC721(self.idToERC721ContractAddress[_contractId]).tokenURI(_tokenId)
    return _uri


@view
@external
def name(_contractId: uint256) -> String[64]:
    assert _contractId <= self.contractCount
    _name: String[64] = "" 
    if self.idToERC20ContractAddress[_contractId] != ZERO_ADDRESS:
        _name = ERC20(self.idToERC20ContractAddress[_contractId]).name()
    else:
        _name = ERC721(self.idToERC721ContractAddress[_contractId]).name()
    return _name


@view
@external
def symbol(_contractId: uint256) -> String[32]:
    assert _contractId <= self.contractCount
    _symbol: String[32] = "" 
    if self.idToERC20ContractAddress[_contractId] != ZERO_ADDRESS:
        _symbol = ERC20(self.idToERC20ContractAddress[_contractId]).symbol()
    else:
        _symbol = ERC721(self.idToERC721ContractAddress[_contractId]).symbol()
    return _symbol


@external
def setBaseURI(_contractId: uint256, _uri: String[256]):
    assert msg.sender == self.minter
    assert _contractId <= self.contractCount
    assert self.idToERC721ContractAddress[_contractId] != ZERO_ADDRESS
    ERC721(self.idToERC721ContractAddress[_contractId]).setBaseURI( _uri)


@view
@external
def totalSupply(_contractId: uint256) -> uint256:
    assert _contractId <= self.contractCount
    _totalSupply: uint256 = 0
    if self.idToERC20ContractAddress[_contractId] != ZERO_ADDRESS:
        _totalSupply = ERC20(self.idToERC20ContractAddress[_contractId]).totalSupply()
    else:
        _totalSupply = ERC721(self.idToERC721ContractAddress[_contractId]).totalSupply()
    return _totalSupply


@external
def self_destruct():
    assert msg.sender == self.minter
    selfdestruct(self.minter)
