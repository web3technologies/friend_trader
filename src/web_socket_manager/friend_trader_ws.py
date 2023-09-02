import json
import os
import django
from decouple import config
import concurrent.futures

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'friend_trader.settings.{config("ENVIRONMENT")}')
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
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        
    def run_coroutine_in_thread(self, coroutine):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coroutine)
        finally:
            loop.close()

    # should this be async?
    def sync_blocks(self, block_hash):
        if self.env in ("int", "prod"):
            print("Checking initial Sync")
            initial_block_num = settings.INITIAL_BLOCK
            current_block = self.web3.eth.get_block(block_hash)
            block_number = current_block.number
            blocks_nums_stored = list(
                Block.objects.filter(block_number__gte=settings.INITIAL_BLOCK, block_number__lte=block_number) \
                .order_by("block_number")\
                .values_list("block_number", flat=True)
            )
            should_have_blocks = [block_num for block_num in range(initial_block_num, block_number+1)]
            missing_blocks = []

            for block_num in should_have_blocks:
                if block_num not in blocks_nums_stored:
                    missing_blocks.append(block_num)
            if missing_blocks:
                print(f"Syncing blocks -- missing: {len(missing_blocks)}")
                block_actions_to_perform = []
                batch_count = 0
                for block_num in missing_blocks:
                    block_actions_to_perform.append(
                        perform_block_actions_task.s(block_number=block_num)
                    )
                    batch_count += 1
                    if batch_count == 250:
                        perform_many_block_actions = group(block_actions_to_perform)
                        perform_many_block_actions.apply_async()
                        block_actions_to_perform = []
                        batch_count = 0
            else:
                print(f"All blocks are synced and up to date")

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
                    loop = asyncio.get_running_loop()
                    loop.run_in_executor(self.executor, self.sync_blocks, block_hash)
                    self.initial = False
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
    asyncio.get_event_loop().run_until_complete(friend_trader.listen_for_new_blocks())


    

    
