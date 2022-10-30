# Extract data from blockchain

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

## Tech

- [Web3] - Python library for interacting with Ethereum
- [Python 3.9] - Release of Python
- [Pipenv] - Tool for creating a virtual environment.
- [QuickNode] - Node provider for interacting with the Ethereum blockchain (mainnet).

## Installation

Install the dependencies in a virtual environment

```sh
pipenv install
pipenv shell
setup.py install
```

## Execution
After executing "*setup.py install*", we can use "*extract_data*" as an executable of this project. The result is a json which is located in "*result_path*" defined in app.config.json. You can see an example in "*extract_data/tests/resources/result.json*".
```sh
extract_data -c extract_data\tests\resources\app-config.json
```

## Configuration file app.config.json
Below is a table showing the parameters' detail defined in app-config.json:

| Parameter | Description | Example |
| ------ | ------ | ------ |
| ethereum_node | Endpoint for this node | https://tame-wild-reel.discover.quiknode.pro/769bab361bdeb21065e0d61af80745652507aa82/ |
| addresses_get_info | Addresses' list for being analyzed | ["0x782de3f99f9c73c125a5e6b494373a3c68a2a914", "0x6830ac58535c7c133cb8cca7f9804fe602be3f5c"] |
| track_history_in_last_blocks | Number of blocks for being queried in order to get the transaction history| 1000000|
| logs_folder | Logs folder where logs files are generated | logs |
| results_path | Result path where the result will be written. | extract_data/tests/resources/results.json |
| erc20_list | List of erc20 tokens for being analyzed. | [{"name": "MATIC", "tokenAddress": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0", "abi_path": "extract_data/tests/resources/abi_files/matic.abi.json"}, {"name": "USDT", "tokenAddress": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "abi_path": "extract_data/tests/resources/abi_files/usdt.abi.json"}] |
| compound_tokens | Definition of all compound tokens found in etherscan. | [{"name": "cUSDC", "0x39AA39c021dfbaE8faC545936693aC917d5E7563": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0", "abi_path": "extract_data/tests/resources/abi_files/cusdc.abi.json"}, {"name": "cDAI", "tokenAddress": "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643", "abi_path": "extract_data/tests/resources/abi_files/cdai.abi.json"}] |
| airdrop_info | Info about the airdrop which will be analyzed in exercise 1.2.2. | {"airdrop_address_example": "0xAd815dB0B31B76B33138482343605E71fa69CB59","airdrop_address_abi": "extract_data/tests/resources/abi_files/airdrop-example.abi.json","airdrop_to_block": 14661136,"airdrop_from_block": 14635446} |


## Folders' structure

```
extract_data
└───logs
└───extract_data
│   └───dashboards --> Dashboards done on Dune Analytics
│   └───main_program
│       │   └───blockchain_interactions
│       │       |   __init__.py
│       │       |   events_contract.py --> Events defined
│       │       |   web3_manager.py --> Interactions using web3 library
│       │   __init__.py
│       │   mainApp.py --> Entry point of the program
│   └───tests
│       │   └───resources
│       │       |   └───abi_files --> Abi files used for reading events in several smart contracts.
│       │       |   app-config.json --> Configuration file
│       │       |   results.json --> Result written at the end of the program
│       │   __init__.py
│       │   test_main_program.py --> Mini tests implemented. 
│   __init__.py  
│   Pipfile   
│   Pipfile.lock     
│   README.md    
│   setup.py  
```

## Answers
- **Question 1**: Given a list of public addresses extract the following: Current balance, current token balance, and/or Transaction history.
Parse the transaction history for token transfers/swaps.
    -   Can you label or classify these wallets in some way. 
- **Answers 1**: 
    - I extracted the current balance of several addresses in ETH, USDT and MATIC. You can add a new token in app.config.json without doing anything else in order to know the balance in that token. 
    - The transaction history was extracted using filters on contracts. I've filtered the transactions by transfers and swaps events. 
    - There're limitations in the quantity of blocks to analyze. Therefore, I had to loop in intervals of 10.000 blocks until <track_history_in_last_blocks> blocks. 
    - I can classify these wallets of different ways:
        - Sorting by swaps or transfers transactions (holder/trader).
        - Smart contract or private address (It's showed in the result json file - Parameter Type).
- **Question 2**: Filter and return protocol relevant on-chain events you may use to analyze a smart contract protocol
    - Example 1: Search for any time a Compound cToken is minted or burned. What timezone do Compound users live in?
    - Example 2: Search for the median claim amount of an airdrop. Sybil attack?
    - Example 3: Search for any time a new LP is made on Osmosis. What’s most popular?
- **Answers 2**
    - Example 1: I found the compound tokens on etherscan https://etherscan.io/labelcloud (Label Compound), and I pasted the information in app-config.json. Mint and Burnt events were filtered in a similar way that I explained in the last exercise. And finally, timestamps were extracted and used for calculating the median to know which could be the timezone. 
    - Example 2: I searched for an address which was used for doing an airdrop (about 151 Get Airdropped event transactions). And the amount was extracted of every claimed. Finally, a median was calculated. 
        - Sybil attacks occur when networked systems get gamed by a few accounts, creating multiple identities. Checking the number of transactions, this airdrop was susceptible of suffering a sybil attack. We can suppose that there are a little quantity of people. Therefore, it's easy to do several movements between accounts for being eligible for the airdrop.
    - Example 3: I haven't done this exercise. But, I've investigated a way to try doing it:
        -  Osmosis is a DEX for the Cosmos ecosystem. Therefore, it's a possibility to use "*cosmpy*" in order to extract data from Cosmos.
        -  Checking app.osmosis.zone website, the most popular LP is ATOM/OSMO.
- **Questions 3**: Wild card, build something clever
    - Example 1: Replicate the Uniswap routing engine, use this to price an Ethereum account token balance in a niche token like PICKLE.
    - Example 2: Create a dashboard for price arbitrage between UniV2 and UniV3.
    - Example 3: Gather data you may use to report on an L1. Staking history & diversity, ecosystem growth, p/e ratios, etc.
- **Answers 3**
    - Example1: -
    - Example2: I did a dashboard using Dune Analytics. Basically, it's a table which it's showed the main data for getting the difference between two prices, and the gain in percentage after executing arbitrage. The pair used was WETH/USDC. You can see this dashboard in "*extract_data/dashboards*"
    - Example3: -
