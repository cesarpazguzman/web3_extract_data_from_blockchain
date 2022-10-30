import argparse
from datetime import datetime
import json
import logging
from typing import List

from web3.contract import Contract

from extract_data.main_program.blockchain_interactions import events_contract
from extract_data.main_program.blockchain_interactions.events_contract import Event
from extract_data.main_program.blockchain_interactions.web3_manager import Web3Manager
from statistics import median
import sys


def read_json(path: str) -> dict:
    """
        Description: Read a path as a json file.
        Args:
            path (str): Path which will be read as a json file

        Returns: The dictionary
    """

    with open(path, 'r') as json_file:
        return json.load(json_file)


def extract_info_addresses(web3_manager, app_config: dict) -> list:
    """
        Description: Extract the needed info for an addresses list
        Args:
            web3_manager (Web3Manager): Manager for getting data from blockchain
            app_config (dict): app-config.json

        Returns: All needed info for an addresses list
    """

    logging.info("Extracting info for all defined addresses.")
    list_info_by_address = []
    for address in app_config["addresses_get_info"]:
        if not web3_manager.w3.isAddress(address):
            logging.error(f"The address {address} is not valid")
            sys.exit(-1)

        info_address = get_info_by_address(web3_manager, app_config, address)
        logging.info(f"Address {address}: {info_address}")
        list_info_by_address.append(info_address)

    return list_info_by_address


def get_info_by_address(web3_manager, app_config: dict, address: str) -> dict:
    """
        Description: Gets the needed info for a specific address
        Args:
            web3_manager (Web3Manager): Manager for getting data from blockchain
            app_config (dict): app-config.json
            address (dict): Address which will be extracted the needed info

        Returns: The needed info for a specific address (Balance, transaction history)
    """

    logging.info(f"Extracting info for {address}.")

    transaction_history_tokens = get_transaction_history_contract(web3_manager, address, app_config)

    res = {
        'Address': address,
        'Type': "Smart contract" if web3_manager.is_address_contract(address) else "Private key address",
        'CurrentBalanceETH': web3_manager.get_current_balance_eth(address)
    }

    for erc20 in app_config["erc20_list"]:
        res.update({
            f"CurrentBalance{erc20['name']}":
                web3_manager.get_current_balance_erc20(erc20['tokenAddress'], address, erc20['name']),
            f"TransfersHistory{erc20['name']}":
                transaction_history_tokens[f"transaction_history_transfers_{erc20['name']}"],
            f"SwapHistory{erc20['name']}":
                transaction_history_tokens[f"transaction_history_swap_{erc20['name']}"]
        })

    return res


def get_transaction_history_contract(web3_manager, address: str, app_config: dict) -> dict:
    """
        Description: Gets all transaction history (transfers, swaps) in a blocks' interval
        Args:
            web3_manager (Web3Manager): Manager for getting data from blockchain
            address (dict): Address which will be extracted the transaction history
            app_config (dict): app-config.json

        Returns: All transaction history (transfers, swaps) in a blocks' interval
    """

    logging.info("Creating all the contract objets.")
    contracts_erc20 = {}
    for erc20 in app_config["erc20_list"]:
        contracts_erc20.update({
            erc20["name"]: web3_manager.get_contract_erc20(erc20['tokenAddress'], erc20["name"])
        })

    latest_block: int = web3_manager.get_latest_block_number()
    batch_size = 9999
    num_iterations = int(app_config["track_history_in_last_blocks"]/batch_size)
    logging.info(f"Transaction history starts: {num_iterations} iterations will be executed.")

    res = {}
    for num_iter in range(0, num_iterations):
        for erc20_name, contract in contracts_erc20.items():
            transaction_history_transfers_token, transaction_history_swap_token = transactions_by_token(
                contract, latest_block-batch_size, latest_block, address, erc20_name, list(contracts_erc20.values())
            )

            if f"transaction_history_transfers_{erc20_name}" in res:
                res[f"transaction_history_transfers_{erc20_name}"] += transaction_history_transfers_token
            else:
                res[f"transaction_history_transfers_{erc20_name}"] = transaction_history_transfers_token

            if f"transaction_history_swap_{erc20_name}" in res:
                res[f"transaction_history_swap_{erc20_name}"] += transaction_history_swap_token
            else:
                res[f"transaction_history_swap_{erc20_name}"] = transaction_history_swap_token

        latest_block = latest_block-batch_size

        if num_iter % 10 == 0:
            logging.info(f"Iteration {num_iter}")

    return res


def transactions_by_token(contract: Contract, from_block: int, to_block: int, address: str, erc20_name: str,
                          all_contracts: List[Contract])\
        -> tuple[list[str], list[str]]:
    """
        Description: Gets the transaction history for address (transfers/swaps) for a specific token
        Args:
            contract (Contract): Contract for being analyzed
            from_block (int): Initial block for being analyzed
            to_block (int): Final block for being analyzed
            address (str): Address which will be extracted the transaction history
            erc20_name (str): Token's name which is being analyzed
            all_contracts(List): For checking if it was happened a swap between two contracts
        Returns: Transaction history for address (transfers/swaps)
    """

    logging.info(f"Getting transaction history (transfers/swap) for {address} using {erc20_name}")
    transaction_history_swaps = []
    transaction_history_transfers = []
    transfers_from = events_contract.get_event_from_contract(
        Event.Transfer, contract, from_block, to_block, erc20_name, {'from': address})
    swaps = events_contract.get_event_from_contract(
        Event.Swap, contract, from_block, to_block, erc20_name, {'from': address})

    for transfer in transfers_from:
        transaction_hash_to = []
        for another_contract in all_contracts:
            transfers_to = events_contract.get_event_from_contract(
                Event.Transfer, another_contract, transfer["blockNumber"],
                transfer["blockNumber"], another_contract.functions.symbol().call(), {'to': address})
            if transfers_to:
                transaction_hash_to.append(transfers_to[0]["transactionHash"].hex())
        if transfer["transactionHash"].hex() not in transaction_hash_to:
            transaction_history_transfers.append(transfer["transactionHash"].hex())
        elif transfer["transactionHash"].hex() in transaction_hash_to:
            transaction_history_swaps.append(transfer["transactionHash"].hex())

    for swap in swaps:
        transaction_history_swaps.append(swap["transactionHash"].hex())

    return transaction_history_transfers, transaction_history_swaps


def get_median_claim_account(web3_manager, app_config: dict) -> list:
    """
        Description: Gets the median claimed quantity in the address used for the airdrop
        Args:
            web3_manager (Web3Manager): Manager for getting data from blockchain
            app_config (dict): app-config.json

        Returns: List[median claimed quantity, number of claimed airdrop event]
    """
    logging.info("Getting the median claimed in a specific airdrop.")
    logging.info("Creating the airdrop's contract object.")
    contract: Contract = web3_manager.get_contract_erc20(
        app_config["airdrop_info"]['airdrop_address_example'], "airdrop")

    latest_block = app_config["airdrop_info"]["airdrop_to_block"]
    batch_size = 9999
    num_iterations = int((latest_block-app_config["airdrop_info"]["airdrop_from_block"]) / batch_size)
    logging.info(f"Transaction history starts: {num_iterations} iterations will be executed")

    claim_quantity = []

    for num_iter in range(0, num_iterations):
        claim_airdrop = events_contract.get_event_from_contract(
            Event.AirDropped, contract, latest_block - batch_size, latest_block, "airdrop")
        for claim in claim_airdrop:
            claim_quantity.append(web3_manager.get_ether_value_from_wei(claim["args"]["amount"]))

        latest_block = latest_block - batch_size

    logging.info(f"For {len(claim_quantity)} getAirdropped event the median claim quantity was {median(claim_quantity)}")
    return [median(claim_quantity), len(claim_quantity)] if claim_quantity else -1


def get_events_compound_token(web3_manager, app_config: dict) -> dict:
    """
        Description: Gets the median time of mint/burnt events for every ctoken
        Args:
            web3_manager (Web3Manager): Manager for getting data from blockchain
            app_config (dict): app-config.json

        Returns: Result of getting data from compounds token
    """
    logging.info("Getting the compound token's median hour for mint/burnt events.")
    logging.info("Creating the ctoken's contract objects.")
    res = {}
    events = {}
    contracts_compound_tokens = {}
    for ctoken in app_config["compound_tokens"]:
        contracts_compound_tokens.update({
            ctoken["name"]: web3_manager.get_contract_erc20(ctoken['tokenAddress'], ctoken["name"])
        })

    logging.info(f"Contracts: {contracts_compound_tokens}")
    latest_block = web3_manager.get_latest_block_number()
    batch_size = 9999
    num_iterations = int(app_config["track_history_in_last_blocks"] / batch_size)
    logging.info(f"Transaction history starts: {num_iterations} iterations will be executed")

    for num_iter in range(0, num_iterations):
        for ctoken, contract in contracts_compound_tokens.items():
            mints = events_contract.get_event_from_contract(
                Event.Mint, contract, latest_block - batch_size, latest_block, ctoken)
            burnt = events_contract.get_event_from_contract(
                Event.Burnt, contract, latest_block - batch_size, latest_block, ctoken)

            if f"transaction_history_mint_{ctoken}" in events:
                events[f"transaction_history_mint_{ctoken}"] += mints
            else:
                events[f"transaction_history_mint_{ctoken}"] = mints

            if f"transaction_history_burnt_{ctoken}" in events:
                events[f"transaction_history_burnt_{ctoken}"] += burnt
            else:
                events[f"transaction_history_burnt_{ctoken}"] = burnt

        latest_block = latest_block - batch_size

        if num_iter % 10 == 0:
            logging.info(f"Iteration {num_iter}")

    logging.info("Calculating the median hour for mint/burnt events of each ctoken.")
    for ctoken, contract in contracts_compound_tokens.items():
        hour_time_mint = []
        hour_time_burnt = []
        for mint in events[f"transaction_history_mint_{ctoken}"]:
            hour_time_mint.append(web3_manager.get_time_hour_from_block(mint["blockNumber"]))

        for burnt in events[f"transaction_history_burnt_{ctoken}"]:
            hour_time_burnt.append(web3_manager.get_time_hour_from_block(burnt["blockNumber"]))

        res[ctoken] = {
            "Mint_time_median": get_time_timezone(median(hour_time_mint) if hour_time_mint else -1),
            "Burnt_time_median": get_time_timezone(median(hour_time_burnt) if hour_time_burnt else -1)
        }

    return res


def get_time_timezone(hour: float) -> str:
    """
        Description: Process the hour to a string format with the timezone.
        Args:
            hour (float): Time for being processed

        Returns: Time formatted with the timezone
    """

    if hour == -1:
        return "N/A"

    minutes = int((hour - int(hour))*60)

    return f"{int(hour)}:{str(minutes).zfill(2)} ({datetime.now().astimezone().tzname()})"


def write_results(result_path: str, info_addresses: dict, claim_airdrop: list,
                  compound_tokens_info: dict, app_config: dict):
    """
        Description: Write the final result of the program in a json file
        Args:
            result_path (str): Path which result will be written
            info_addresses (dict): The result of getting info of the addresses list
            claim_airdrop (dict): Info about the airdrop
            compound_tokens_info (dict): Median of times of each ctoken
            app_config (dict): app-config.json

        Returns:
            None
    """
    logging.info(f"Writing the results in {result_path}.")

    res = {"TrackingAddresses": {},
           "CompoundTokensTimeMintBurnt": compound_tokens_info,
           "AirdropInfo": {"Airdrop_address": app_config["airdrop_info"]["airdrop_address_example"],
                              "Number_claims": claim_airdrop[1],
                              "Median_claimed": claim_airdrop[0]}}

    for info_address in info_addresses:
        res_address = {
            "Type": info_address["Type"],
            "CurrentBalanceETH": info_address["CurrentBalanceETH"]
        }

        res_erc20 = {}
        for erc20 in app_config["erc20_list"]:
            res_erc20[erc20["name"]] = {
                "CurrentBalance": info_address[f"CurrentBalance{erc20['name']}"],
                "TransactionsHistory": {
                    "Transfers": info_address[f"TransfersHistory{erc20['name']}"],
                    "Swaps": info_address[f"SwapHistory{erc20['name']}"]
                }
            }

        res_address["DetailsERC20"] = res_erc20

        res["TrackingAddresses"].update({info_address["Address"]: res_address})

    with open(result_path, "w") as outfile:
        json.dump(res, outfile, indent=4)


def main():
    """
        Description: The entry point of the program
        Args: -c <path_appconfig>
    """

    parser = argparse.ArgumentParser(prog='infoAddresses_program')
    parser.add_argument('-c', nargs='?', help='properties file path')
    args = parser.parse_args()
    configs = read_json(args.c)

    print(f"Starting program. Logs generated in {configs['logs_folder']}/main_program.log")
    logging.basicConfig(filename=f'{configs["logs_folder"]}/main_program.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logging.info('Program started')

    web3_manager = Web3Manager(configs)

    info_addresses = extract_info_addresses(web3_manager, configs)
    claim_airdrop = get_median_claim_account(web3_manager, configs)
    compound_token_info = get_events_compound_token(web3_manager, configs)

    write_results(configs["results_path"], info_addresses, claim_airdrop, compound_token_info, configs)

    logging.info('Finished')
    print(f"Finished. Results generated in {configs['results_path']}")
