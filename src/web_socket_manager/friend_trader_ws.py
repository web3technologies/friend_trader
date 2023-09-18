#!/applications/friend_trader/venv/bin/python3
import json
import os
import django
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'friend_trader.settings.{config("ENVIRONMENT")}')
django.setup()
from django.conf import settings
import asyncio
from asyncio.exceptions import TimeoutError, IncompleteReadError
import websockets
from websockets.exceptions import ConnectionClosed, ConnectionClosedError
from web3 import Web3

from friend_trader_async.tasks import chained_block_actions_task, sync_blocks_task


class FriendTraderListener:
    blast_wss = f"wss://base-mainnet.blastapi.io/{settings.BLAST_WSS_API}"
    env = config("ENVIRONMENT")
    blast_url = f"https://base-mainnet.blastapi.io/{settings.BLAST_WSS_API}"
    web3 = Web3(Web3.HTTPProvider(blast_url))

    def __init__(self) -> None:
        self.initial = True

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
                block_num_hex = json.loads(message).get('params').get('result').get("number")
                block_number = int(block_num_hex, 16)
                print(f"Block# {block_number}")
                if self.initial and self.env in ("int", "prod"):
                    print("performing initial sync")
                    sync_blocks_task.delay(block_number=block_number)
                    self.initial = False
                else:
                    chained_block_actions_task.delay(block_number=block_number)
                
    async def listen_for_new_blocks(self):
        while True:
            try:
                await self.handle_connection()
            except (ConnectionClosed, ConnectionClosedError, TimeoutError, IncompleteReadError):
                print("Connection lost. Reconnecting in 5 seconds...")
                self.initial = True
                await asyncio.sleep(5)  # wait for 5 seconds before retrying
            except Exception as e:
                self.initial = True
                print(f"Error: {e}")
                await asyncio.sleep(5) 
        

if __name__ == "__main__":
    friend_trader = FriendTraderListener()
    asyncio.get_event_loop().run_until_complete(friend_trader.listen_for_new_blocks())


    

    
