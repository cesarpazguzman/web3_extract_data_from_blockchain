import json
import logging
import sys

from hexbytes import HexBytes
from web3 import Web3, HTTPProvider
from web3.contract import Contract
from datetime import datetime


class Web3Manager:
    def __init__(self, app_config: str):
        logging.info("Initializing web3 manager.")

        logging.info(f"Getting endpoint {app_config['ethereum_node']}")
        self.w3 = Web3(HTTPProvider(app_config["ethereum_node"]))
        if not self.w3.isConnected():
            logging.error("Error connecting to endpoint")
            raise Exception("Error connecting to endpoint")

        logging.info("Endpoint read successfully.")
        logging.info("Reading abi_files")
        self.abi_files = {}
        for erc20_token in app_config["erc20_list"]:
            with open(erc20_token['abi_path'], 'r') as json_file:
                self.abi_files[erc20_token["name"]] = json.load(json_file)
        for ctoken in app_config["compound_tokens"]:
            with open(ctoken['abi_path'], 'r') as json_file:
                self.abi_files[ctoken["name"]] = json.load(json_file)

        with open(app_config["airdrop_info"]["airdrop_address_abi"], 'r') as json_file:
            self.abi_files["airdrop"] = json.load(json_file)

        logging.info("Abi files successfully read.")

    def get_current_balance_eth(self, address: str) -> float:
        """
            Description: Gets the current balance in ETH
            Args:
                address (str): Address which we can get the info

            Returns: The current balance in ETH
        """
        logging.info(f"Getting the {address}'s current balance in ETH")
        return float(self.w3.fromWei(self.w3.eth.get_balance(Web3.toChecksumAddress(address)), 'ether'))

    def get_current_balance_erc20(self, token_address: str, address: str, name_token: str) -> float:
        """
            Description: Gets the current balance of every defined erc20 tokens
            Args:
                token_address (str): Smart Contract's address
                address (str): Address which we can get the info
                name_token (str): Token's name

            Returns: The current balance of every defined erc20 tokens
        """
        logging.info(f"Getting the {address}'s current balance in {name_token}")
        return float(self.w3.fromWei(self.w3.eth.contract(
            Web3.toChecksumAddress(token_address), abi=self.abi_files[name_token]).functions.balanceOf(
            Web3.toChecksumAddress(address)).call(), 'ether'))

    def get_contract_erc20(self, token_address: str, name_token: str) -> Contract:
        """
            Description: Gets the smart contract object
            Args:
                token_address (str): Smart Contract's address
                name_token (str): Token's name

            Returns: The smart contract object
        """
        logging.info(f"Contract object ({name_token}) created for being analyzed.")
        return self.w3.eth.contract(Web3.toChecksumAddress(token_address), abi=self.abi_files[name_token])

    def get_latest_block_number(self) -> int:
        """
            Description: Gets the latest blockNumber of the blockchain
            Args: None

            Returns: The latest blockNumber of the blockchain
        """
        return self.w3.eth.block_number

    @staticmethod
    def get_symbol_contract(contract: Contract) -> str:
        """
            Description: Gets the token's symbol associated with the contract
            Args:
                contract (str): Smart Contract's object

            Returns: The token's symbol associated with the contract
        """
        return contract.functions.symbol().call()

    def is_address_contract(self, address: str) -> bool:
        """
            Description: Checks if the address is valid or not
            Args:
                address (str): Address which we can get the info

            Returns: If the address is valid or not
        """
        return self.w3.eth.getCode(Web3.toChecksumAddress(address)) != HexBytes('0x')

    def get_time_hour_from_block(self, block_number: int) -> float:
        """
            Description: Gets the hour:minute of a specific block_number
            Args:
                block_number (str): BlockNumber for getting the timestamp

            Returns: The hour:minute of a specific block_number
        """
        dt_block = datetime.fromtimestamp(self.w3.eth.getBlock(block_number).timestamp)
        return round(dt_block.hour+dt_block.minute/60.0, 2)

    def get_ether_value_from_wei(self, wei_value):
        """
            Description: Converts a wei value in a ether value
            Args:
                wei_value (int): Wei value which we can convert

            Returns: Ether value
        """
        return float(self.w3.fromWei(wei_value, 'ether'))
