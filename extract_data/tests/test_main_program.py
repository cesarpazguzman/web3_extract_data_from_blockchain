import json

import pytest

from extract_data.main_program.blockchain_interactions import events_contract
from extract_data.main_program.blockchain_interactions.events_contract import Event
from extract_data.main_program.blockchain_interactions.web3_manager import Web3Manager


def read_app_config():
    with open('extract_data/tests/resources/app-config.json', 'r') as json_file:
        return json.load(json_file)


def test_exist_transfer_events():
    web3_manager = Web3Manager(read_app_config())
    contract = web3_manager.get_contract_erc20("0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0", "MATIC")
    transfer_events = events_contract.get_event_from_contract(
        type_event=Event.Transfer, contract=contract, from_block=15812610, to_block=15812610, name_token="MATIC",
        argument_filters={'from': '0x5d260e01805af8b848f0b627e43951ea18336267'})

    assert len(transfer_events) > 0


def test_exist_swaps_events():
    web3_manager = Web3Manager(read_app_config())
    address = "0x6830ac58535c7c133cb8cca7f9804fe602be3f5c"
    block_number = 15810534
    contract_usdt = web3_manager.get_contract_erc20("0xdAC17F958D2ee523a2206206994597C13D831ec7", "USDT")
    transfer_events_usdt = events_contract.get_event_from_contract(
        type_event=Event.Transfer, contract=contract_usdt, from_block=block_number, to_block=block_number,
        name_token="USDT", argument_filters={'from': address})

    contract_matic = web3_manager.get_contract_erc20("0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0", "MATIC")
    transfer_events_matic = events_contract.get_event_from_contract(
        type_event=Event.Transfer, contract=contract_matic, from_block=block_number, to_block=block_number,
        name_token="MATIC", argument_filters={'to': address})

    assert len(transfer_events_usdt) > 0 and len(transfer_events_matic) > 0


def test_contract_symbol():
    web3_manager = Web3Manager(read_app_config())
    contract = web3_manager.get_contract_erc20("0xdAC17F958D2ee523a2206206994597C13D831ec7", "USDT")
    assert web3_manager.get_symbol_contract(contract) == "USDT"
