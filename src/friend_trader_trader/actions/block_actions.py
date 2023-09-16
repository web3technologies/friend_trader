import json
import random
from web3 import Web3

from django.db import transaction
from django.conf import settings
from django.utils import timezone

from friend_trader_trader.models import Block, FriendTechUser, Trade, Price


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
        self.shares_subject_cache = {}
        self.user_data = []
        self.prices_to_create = []
        self.trades_to_update = []
        
    @property
    def function_handler(self):
        return {
            "buyShares": self.__buy_or_sell_shares,
            "sellShares": self.__buy_or_sell_shares
        }
        
    def __individual_share_prices(self, post_transaction_supply, amount, is_buy):
        def get_price(supply, amount):
            sum1 = 0 if supply == 0 else (supply - 1) * supply * (2 * (supply - 1) + 1) // 6
            sum2 = 0 if supply == 0 and amount == 1 else (supply - 1 + amount) * (supply + amount) * (2 * (supply - 1 + amount) + 1) // 6
            summation = sum2 - sum1
            return summation * 1e18 // 16000  # Assuming 1e18 represents 1 ether

        if is_buy:
            supply = post_transaction_supply - amount
        else:
            supply = post_transaction_supply + amount
         
        prices = []
        for i in range(1, amount + 1):
            price = self.web3.from_wei(get_price(supply, i) - get_price(supply, i-1), "ether")
            prices.append(price)
            supply += 1

        return prices

    def __buy_or_sell_shares(self, trade_events, tx_hash):
        for event in trade_events:
            trader = event["args"]["trader"]
            subject = event['args']['subject']
            is_buy = event['args']['isBuy']
            purchase_amount = event['args']['shareAmount']
            
            # this means a call was made to the contract but a purchase was not made
            if purchase_amount == 0:
                continue
            
            # price that was calculated by the contract
            share_price = self.web3.from_wei(event["args"]["ethAmount"], "ether")
            protocol_fee = self.web3.from_wei(event["args"]["protocolEthAmount"], "ether")
            subject_fee = self.web3.from_wei(event["args"]["subjectEthAmount"], "ether")
            post_transaction_supply = event["args"]["supply"]
            
            if subject not in self.shares_subject_cache:
                friend_tech_user, _ = FriendTechUser.objects.get_or_create(address=subject)
                # get share supply from last block
                # expensive but reliable
                #friend_tech_user.shares_supply = self.contract.functions.sharesSupply(friend_tech_user.address).call(block_identifier=self.block_number - 1)
                self.shares_subject_cache[subject] = friend_tech_user
            else:
                friend_tech_user = self.shares_subject_cache[subject]
                
            if purchase_amount > 1:
                prices = self.__individual_share_prices(post_transaction_supply, purchase_amount, is_buy)
            else:
                prices = [share_price]
            
            friend_tech_user.shares_supply = post_transaction_supply
            friend_tech_user.save(update_fields=["shares_supply"])
            
            default_values = {
                "trader": FriendTechUser.objects.get_or_create(address=trader)[0],
                "subject": friend_tech_user,
                "is_buy": is_buy,
                "share_amount": purchase_amount,
                "price": prices[0],
                "protocol_fee": protocol_fee,
                "subject_fee": subject_fee,
                "supply": post_transaction_supply,
                "block": self.block,
            }

            trade, created = Trade.objects.get_or_create(
                    hash=tx_hash.hex(),
                    defaults=default_values
                )
            if created:
                prices_to_create = [Price(trade=trade, price=price) for price in prices]
                self.prices_to_create.extend(prices_to_create)
            # consistency checking
            # if the trade already exists ensure the prices are the same else delete and update values
            else:
                if len(trade.prices.all()) != len(prices):
                    trade.prices.all().delete()
                    for key, value in default_values.items():
                        if hasattr(trade, key):
                            setattr(trade, key, value)
                    self.trades_to_update.append(trade)
                    
            if friend_tech_user.id not in self.user_data:
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
            if self.prices_to_create:
                Price.objects.bulk_create(self.prices_to_create)
            if self.trades_to_update:
                Trade.objects.bulk_update(self.trades_to_update, [
                    "trader", "subject", "is_buy", "share_amount", "price", "protocol_fee", "subject_fee", "supply", "block"
                ])
            
            self.block.date_sniffed = timezone.now()
            self.block.save(update_fields=["date_sniffed"])
            
            
    
    def run(self):
        self.__perform_block_actions()
        self.__handle_post_processing_db_updates()
        return self.user_data