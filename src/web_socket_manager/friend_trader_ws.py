import json
import os
import django
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'friend_trader.settings.{config("ENVIORNMENT")}')
django.setup()
from django.conf import settings
from celery import group 
import asyncio
import websockets
from web3 import Web3

from friend_trader_trader.models import Block
from friend_trader_dispatcher.tasks import perform_block_actions_task


class FriendTraderListener:
    blast_wss = f"wss://base-mainnet.blastapi.io/{settings.BLAST_WSS_API}"
    env = config("ENVIRONMENT")
    blast_url = f"https://base-mainnet.blastapi.io/{settings.BLAST_WSS_API}"
    web3 = Web3(Web3.HTTPProvider(blast_url))

    def __init__(self) -> None:
        self.initial = True

    # should this be async?
    async def sync_blocks(self, block_hash):
        if self.env in ("int", "prod"):
            print("syncing blocks")
            latest_block_number = self.web3.get_block(block_hash).block_number
            
            blocks_stored = list(Block.objects.filter(block_number__gte=settings.INITIAL_BLOCK, block_number__lte=latest_block_number).order_by("block_number").values_list("block_number", flat=True))
            should_have_blocks = [block_num for block_num in range(i,latest_block_number)]
            need_blocks = []
            
            for block_num in should_have_blocks:
                if block_num not in blocks_stored:
                    need_blocks.append(block_num)
            
            block_actions_to_perform = []
            batch_count = 0
            for block_num in need_blocks:
                block_actions_to_perform.append(
                    perform_block_actions_task.s(block_number=block_num)
                )
                batch_count += 1
                if batch_count == 250:
                    perform_many_block_actions = group(block_actions_to_perform)
                    perform_many_block_actions.apply_async()
                    block_actions_to_perform = []
                    batch_count = 0
                i += 1
                    


    async def handle_connection(self):
        
        async with websockets.connect(self.blast_wss) as ws:
            await ws.send(json.dumps({
                "id": 1,
                "jsonrpc": "2.0",
                "method": "eth_subscribe",
                "params": ["newHeads"]
                }
            ))
            message = await ws.recv()
            while True:
                message = await ws.recv()
                block_hash = json.loads(message).get('params').get('result').get("hash")
                print(block_hash)
                if self.initial:
                    self.sync_blocks(block_hash)
                    self.initial=False
                    continue
                else:
                    perform_block_actions_task.delay(block_hash=block_hash, send_notifications=True)
                
    async def listen_for_new_blocks(self):
        try:      
            await self.handle_connection()
        except (websockets.ConnectionClosed, websockets.ConnectionClosedError):
            print("Connection lost. Reconnecting...")
            await self.handle_connection()
        except Exception as e:
            print(f"Error: {e}")
        

if __name__ == "__main__":
    friend_trader = FriendTraderListener()
    friend_trader.sync_blocks()
    asyncio.get_event_loop().run_until_complete(friend_trader.listen_for_new_blocks())


    

    
