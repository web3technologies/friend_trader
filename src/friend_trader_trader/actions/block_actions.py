import json
import random
from web3 import Web3

from django.db import transaction
from django.conf import settings
from django.utils import timezone

from friend_trader_trader.models import Block, FriendTechUser,  Trade



class BlockActions:
    blast_url = f"https://base-mainnet.blastapi.io/{settings.BLAST_WSS_API}"
    ankr_url = "https://rpc.ankr.com/base"
    CONTRACT_ADDRESS = "0xCF205808Ed36593aa40a44F10c7f7C2F67d4A4d4"
    SUCCESSFUL_TRANSACTION_IDENTIFIER = 1

    with open(settings.BASE_DIR / "src" / "web_socket_manager" / "abi.json", "r") as abis:
        contract_abis = json.loads(abis.read())

    web3_providers = [
            # Web3(Web3.HTTPProvider(ankr_url)),
            Web3(Web3.HTTPProvider(blast_url))
        ]
    
    def __init__(self, task, block_number=None) -> None:
        self.task = task
        self.block_number = block_number
        self.block = Block.objects.get_or_create(block_number=block_number)[0]
        self.web3 = random.choice(self.web3_providers)
        self.contract = self.web3.eth.contract(address=self.CONTRACT_ADDRESS, abi=self.contract_abis)
        self.trades_to_create = []
        self.shares_subject_cache = {}
        self.user_data = []
        
    @property
    def function_handler(self):
        return {
            "buyShares": self.__buy_or_sell_shares,
            "sellShares": self.__buy_or_sell_shares
        }

    def __buy_or_sell_shares(self, trade_events, tx_hash):
        for event in trade_events:
            trader = event["args"]["trader"]
            subject = event['args']['subject']
            is_buy = event['args']['isBuy']
            share_amount = event['args']['shareAmount']
            # price that was calculated by the contract
            share_price = self.web3.from_wei(event["args"]["ethAmount"], "ether")
            protocol_fee = self.web3.from_wei(event["args"]["protocolEthAmount"], "ether")
            subject_fee = self.web3.from_wei(event["args"]["subjectEthAmount"], "ether")
            supply = event["args"]["supply"]
            
            if subject not in self.shares_subject_cache:
                friend_tech_user, _ = FriendTechUser.objects.get_or_create(address=subject)
                # get share supply from last block
                # expensive but reliable
                friend_tech_user.shares_supply = self.contract.functions.sharesSupply(friend_tech_user.address).call(block_identifier=self.block_number - 1)
                self.shares_subject_cache[subject] = friend_tech_user
            else:
                friend_tech_user = self.shares_subject_cache[subject]

            friend_tech_user.shares_supply = supply
            friend_tech_user.save(update_fields=["shares_supply"])
            trade = Trade(
                trader=FriendTechUser.objects.get_or_create(address=trader)[0],
                subject=friend_tech_user,
                is_buy=is_buy,
                share_amount=share_amount,
                price=share_price,
                protocol_fee=protocol_fee,
                subject_fee=subject_fee,
                supply=supply,
                block=self.block,
                hash=tx_hash.hex()
            )
            self.trades_to_create.append(trade)
            self.user_data.append(friend_tech_user.id)
        
        
    def __perform_block_actions(self):
        fetched_block = self.web3.eth.get_block(self.block_number, full_transactions=True)
        self.block.block_timestamp = fetched_block.timestamp
        self.block.block_hash = fetched_block.hash.hex()
        self.block.save(update_fields=["block_timestamp", "block_hash"])
        print(f"Block # {fetched_block.number}")
        for tx in fetched_block.transactions:
            # if transaction is to the address and it is successful
            if tx["to"] == self.contract.address and self.web3.eth.get_transaction_receipt(tx.hash)["status"] == self.SUCCESSFUL_TRANSACTION_IDENTIFIER:
                function, function_input = self.contract.decode_function_input(tx.input)
                if function.function_identifier in self.function_handler:
                    trade_events = self.contract.events.Trade().process_receipt(self.web3.eth.get_transaction_receipt(tx.hash))
                    self.function_handler[function.function_identifier](trade_events, tx.hash)
                    

    def __handle_post_processing_db_updates(self):
        with transaction.atomic():
            if self.trades_to_create:
                Trade.objects.bulk_create(self.trades_to_create)
            self.block.date_sniffed = timezone.now()
            self.block.save(update_fields=["date_sniffed"])
            
    
    def run(self):
        self.__perform_block_actions()
        self.__handle_post_processing_db_updates()
        return self.user_data