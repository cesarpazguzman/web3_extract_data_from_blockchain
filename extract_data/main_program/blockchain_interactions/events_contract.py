import logging
from typing import List

from web3.contract import Contract
from web3.types import LogReceipt

from enum import Enum, unique, auto


@unique
class Event(Enum):
    Transfer = auto()
    Swap = auto()
    Mint = auto()
    Burnt = auto()
    AirDropped = auto()


def get_event_from_contract(type_event: Event, contract: Contract, from_block: int, to_block: int, name_token: str,
                            argument_filters: dict = None) -> List[LogReceipt]:
    """
        Description: Gets events in the specified contract and in the specified blocks' interval
        Args:
            type_event (Event): Event which will be searched
            contract (Contract): Contract for being analyzed
            from_block (int): Initial block for being analyzed
            to_block (int): Final block for being analyzed
            argument_filters (dict): Filters for being applied in the search
            name_token (str): Token's name which is being analyzed

        Returns: Events in the specified contract and in the specified blocks' interval
    """

    logging.info(f"Checking if {type_event.name} is defined in the abi file's contract ({name_token}).")
    if type_event.name not in [event["name"] for event in contract.events.__dict__['_events']]:
        logging.info(f"The event {type_event.name} is not in contract ({name_token})")
        return []
    logging.info(f"{type_event.name} event filter in execution (fromBlock={from_block}, toBlock={to_block},"
                 f"argument_filters={argument_filters}).")

    if type_event == Event.Transfer:
        return contract.events.Transfer.createFilter(
            fromBlock=from_block,
            toBlock=to_block,
            argument_filters=argument_filters).get_all_entries()
    elif type_event == Event.Swap:
        return contract.events.Swap.createFilter(
            fromBlock=from_block,
            toBlock=to_block,
            argument_filters=argument_filters).get_all_entries()
    elif type_event == Event.Mint:
        return contract.events.Mint.createFilter(
            fromBlock=from_block,
            toBlock=to_block).get_all_entries()
    elif type_event == Event.Burnt:
        return contract.events.Burnt.createFilter(
            fromBlock=from_block,
            toBlock=to_block).get_all_entries()
    elif type_event == Event.AirDropped:
        return contract.events.AirDropped.createFilter(
            fromBlock=from_block,
            toBlock=to_block).get_all_entries()
